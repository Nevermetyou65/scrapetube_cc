"""Module for fetching and processing Thai language YouTube video subtitles using youtube_transcript_api."""

import random
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import threading

import pandas as pd
from loguru import logger
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
    FetchedTranscript,
)
from tqdm.auto import tqdm


def fetch_thai_youtube_transcript(video_id: str, **kwargs) -> FetchedTranscript | None:
    """Fetch Thai language transcript for a YouTube video."""
    try:
        ytt_api = YouTubeTranscriptApi(**kwargs)
        transcript_list = ytt_api.list(video_id)
        transcript = transcript_list.find_transcript(["th"])
        return transcript.fetch()
    except NoTranscriptFound:
        logger.warning(f"No Thai subs for {video_id}")
        return None
    except TranscriptsDisabled:
        logger.warning(f"Subs disabled for {video_id}")
        return None
    except Exception as e:
        logger.error(f"Subtitle error {video_id}: {str(e)}", exc_info=True)
        return None


def _save_to_parquet(
    df: pd.DataFrame, file_path_parquet: str | Path, lock: threading.Lock
) -> None:
    """Save a DataFrame to a parquet file, appending if possible."""
    with lock:
        try:
            df.to_parquet(
                file_path_parquet, engine="fastparquet", index=False, append=True
            )
            logger.info(f"Saved {len(df)} to {file_path_parquet}")
        except FileNotFoundError:
            df.to_parquet(file_path_parquet, engine="fastparquet", index=False)
            logger.info(f"Created {file_path_parquet}, saved {len(df)}")
        except Exception as e:
            logger.error(f"Parquet save error {file_path_parquet}: {e}")


def get_video_transcript_data(
    video_id: str, sleep_min: int = 1, sleep_max: int = 10, **kwargs
) -> dict:
    """Fetch YouTube video transcript data with rate limiting."""
    sleep_duration = random.randint(sleep_min, sleep_max)
    time.sleep(sleep_duration)

    fetched_transcript = fetch_thai_youtube_transcript(video_id, **kwargs)

    if fetched_transcript is None:
        return {
            "video_id": video_id,
            "is_generated": None,
            "subtitles": None,
        }

    is_generated = fetched_transcript.is_generated
    formatted_subtitles = [
        {
            "text": snippet.text,
            "start": snippet.start,
            "end": snippet.start + snippet.duration,
        }
        for snippet in fetched_transcript.snippets
    ]
    return {
        "video_id": video_id,
        "is_generated": is_generated,
        "subtitles": json.dumps(formatted_subtitles, ensure_ascii=False),
    }


def get_video_transcripts_concurrent(
    video_ids: list[str],
    file_path_parquet: str | Path,
    batch_size: int = 64,
    max_workers: int | None = None,
    sleep_min: int = 1,
    sleep_max: int = 10,
    **kwargs,
):
    """
    Fetch YouTube video transcripts concurrently and save them to a Parquet file in batches.
    """
    if not video_ids:
        return

    logger.info(f"Start fetching {len(video_ids)} videos (max_workers={max_workers})")

    results_batch = []
    lock = threading.Lock()
    processed_count = 0
    total_videos = len(video_ids)

    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="transcript-worker"
    ) as executor:
        future_to_video_id = {
            executor.submit(
                get_video_transcript_data,
                video_id,
                sleep_min=sleep_min,
                sleep_max=sleep_max,
                **kwargs,
            ): video_id
            for video_id in video_ids
        }

        for future in tqdm(
            as_completed(future_to_video_id), total=len(future_to_video_id)
        ):
            video_id = future_to_video_id[future]
            try:
                result = future.result()
                if result and result.get("subtitles"):
                    results_batch.append(result)

                if len(results_batch) >= batch_size:
                    _save_to_parquet(
                        pd.DataFrame(results_batch), file_path_parquet, lock
                    )
                    results_batch = []

            except Exception as exc:
                logger.error(f"Error video {video_id}: {exc}", exc_info=True)
            finally:
                processed_count += 1
                logger.info(f"Done {processed_count}/{total_videos}")

    if results_batch:
        _save_to_parquet(pd.DataFrame(results_batch), file_path_parquet, lock)

    logger.info(f"Finished {processed_count}/{total_videos} videos")
