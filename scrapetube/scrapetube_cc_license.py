import sys
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, NewType

import yt_dlp
from loguru import logger

YoutubeUrl = NewType("YoutubeUrl", str)
NO_LICENSE = "NO_LICENSE"

class YtDlpLoguruLogger:
    def debug(self, msg: str) -> None:
        logger.debug(msg)

    def info(self, msg: str) -> None:
        logger.info(msg)

    def warning(self, msg: str) -> None:
        logger.warning(msg)

    def error(self, msg: str) -> None:
        logger.error(msg)

    def critical(self, msg: str) -> None:
        logger.critical(msg)


def check_license_and_sub(
    video_url: YoutubeUrl,
) -> dict[str, Any]:
    """Extract video information using yt_dlp and return license and subtitle status."""
    try:
        ydl_opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "logger": YtDlpLoguruLogger(),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(str(video_url), download=False, process=False)

        license_val = info.get("license") or NO_LICENSE
        has_subtitles = bool(info.get("subtitles"))
        has_auto_captions = bool(info.get("automatic_captions"))
        has_sub = has_subtitles or has_auto_captions

        return {
            "video_url": str(video_url),
            "license": license_val,
            "has_sub": has_sub,
            "has_manual_subtitles": has_subtitles,
            "has_auto_captions": has_auto_captions,
            "success": True,
        }
    except Exception as exc:  # noqa: BLE001 - we want to surface any yt_dlp errors
        logger.error(f"Failed to extract info for {video_url}: {exc}")
        raise


def process_video(
    video_url: YoutubeUrl,
    *,
    sleep: tuple[int, int],
) -> dict[str, Any]:
    """Process a single video with error handling and rate limiting."""
    try:
        sleep_duration = random.randint(*sleep)
        time.sleep(sleep_duration)
        result = check_license_and_sub(video_url)
        return result
    except Exception as exc:
        logger.error(f"Error processing video {video_url}: {exc}")
        return {
            "video_url": str(video_url),
            "license": NO_LICENSE,
            "has_sub": False,
            "has_manual_subtitles": False,
            "has_auto_captions": False,
            "success": False,
            "error": str(exc),
        }


def process_videos_concurrent(
    video_urls: list[YoutubeUrl],
    *,
    sleep: tuple[int, int] = (5, 25),
    max_workers: int = None,
) -> list[dict[str, Any]]:
    """Process multiple videos concurrently using a bounded thread pool."""
    url_list: list[YoutubeUrl] = [YoutubeUrl(str(u)) for u in video_urls]
    if not url_list:
        return []

    logger.info(
        f"Starting concurrent processing for {len(url_list)} videos with max_workers={max_workers}"
    )

    results: list[dict[str, Any]] = [{} for _ in range(len(url_list))]

    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="yt-worker"
    ) as executor:
        future_to_index = {
            executor.submit(
                process_video,
                url,
                sleep=sleep,
            ): idx
            for idx, url in enumerate(url_list)
        }

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            url = url_list[idx]
            try:
                results[idx] = future.result()
            except (
                Exception
            ) as exc:  # Defensive: `process_video` already catches, but keep robust
                logger.error(f"Unhandled exception for {url}: {exc}")
                results[idx] = {
                    "video_url": str(url),
                    "license": NO_LICENSE,
                    "has_sub": False,
                    "has_manual_subtitles": False,
                    "has_auto_captions": False,
                    "success": False,
                    "error": str(exc),
                }

    logger.info("Finished concurrent processing")
    return results
