"""Wrapper for scrapetube to extract YouTube video metadata."""

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from loguru import logger
from tqdm.auto import tqdm

from scrapetube.scrapetube import get_search_creative_commons


def save_to_parquet(df: pd.DataFrame, file_path_parquet: str | Path) -> None:
    """Save a DataFrame to a parquet file, appending if possible."""
    try:
        df.to_parquet(file_path_parquet, engine="fastparquet", index=False, append=True)
    except FileNotFoundError:
        df.to_parquet(file_path_parquet, engine="fastparquet", index=False)
    except Exception as e:
        logger.error(f"Save error {file_path_parquet}: {e}")


def extract_video_metadata(video_meta: dict) -> dict | None:
    """Extract relevant metadata fields from a video metadata dictionary."""
    try:
        video_id = video_meta.get("videoId", "").strip()

        title_data = video_meta.get("title", {})
        runs = title_data.get("runs", [])
        title = runs[0].get("text", "").strip()

        byline_data = video_meta.get("longBylineText", {})
        runs = byline_data.get("runs", [])
        channel = runs[0].get("text", "").strip()
        nav_endpoint = runs[0].get("navigationEndpoint", {})
        browse_endpoint = nav_endpoint.get("browseEndpoint", {})
        at_channel = browse_endpoint.get("canonicalBaseUrl", "").strip()

        view_count_data = video_meta.get("viewCountText", {})
        view_count = view_count_data.get("simpleText", "")

        return {
            "video_id": video_id or None,
            "title": title or None,
            "channel": channel or None,
            "at_channel": at_channel or None,
            "view_count": view_count or None,
        }

    except Exception as e:
        logger.debug(f"Extract error: {e}")
        return None


def make_request(
    query: str,
    limit: int,
    sleep: tuple[int, int],
    sp_filter: str,
    results_type: str,
    proxies: dict,
) -> list[dict]:
    """Make a request to get video metadata using the scrapetube module."""
    try:
        video_meta_generator = get_search_creative_commons(
            query=query,
            limit=limit,
            sleep=sleep,
            sp_filter=sp_filter,
            results_type=results_type,
            proxies=proxies,
        )
        video_meta_list = list(video_meta_generator)
        return video_meta_list

    except Exception as e:
        logger.error(f"Request failed '{query}': {e}")
        return []


def process_video_metadata(
    video_meta_list: list[dict],
    query: str,
    video_base_url: str,
) -> list[dict]:
    """Process a list of video metadata dictionaries and extract relevant fields."""
    items = []
    successful_extractions = 0
    logger.info(f"Processing {len(video_meta_list)} for '{query}'")
    for video_meta in video_meta_list:
        extracted_data = extract_video_metadata(video_meta)
        if extracted_data:
            extracted_data.update(
                {
                    "query": query,
                    "video_url": f"{video_base_url}{extracted_data['video_id']}",
                    "raw_data": json.dumps(video_meta, ensure_ascii=False),
                }
            )
            items.append(extracted_data)
            successful_extractions += 1

    logger.info(
        f"Extracted {successful_extractions}/{len(video_meta_list)} for '{query}'"
    )
    return items


def collect_and_save_video_metadata(
    query: str,
    limit: int,
    sleep: tuple[int, int],
    sp_filter: str,
    results_type: str,
    proxies: dict,
    video_base_url: str,
    file_path_parquet: str | Path,
) -> None:
    """Collect video metadata for a query and save the results to a parquet file."""
    logger.info(f"Searching: {query}")
    video_meta_list = make_request(
        query, limit, sleep, sp_filter, results_type, proxies
    )
    if video_meta_list:
        logger.info(f"Found {len(video_meta_list)} for '{query}'")

    else:
        logger.warning(f"No results: '{query}'")
        return

    items = process_video_metadata(video_meta_list, query, video_base_url)

    if items:
        save_to_parquet(pd.DataFrame(items), file_path_parquet)
    else:
        logger.warning(f"No valid items: '{query}'")


def save_to_parquet_thread_safe(
    df: pd.DataFrame, file_path_parquet: str | Path, lock: threading.Lock
) -> None:
    """Save a DataFrame to a parquet file, appending if possible (thread-safe)."""
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
            logger.error(f"Save error {file_path_parquet}: {e}")


def process_single_query(
    query: str,
    limit: int,
    sleep: tuple[int, int],
    sp_filter: str,
    results_type: str,
    proxies: dict,
    video_base_url: str,
    file_path_parquet: str | Path,
    lock: threading.Lock,
) -> dict:
    """Process a single query and return the results with metadata."""
    try:
        video_meta_list = make_request(
            query, limit, sleep, sp_filter, results_type, proxies
        )

        if not video_meta_list:
            return {
                "query": query,
                "success": False,
                "items_count": 0,
                "error": "No results found",
            }
        items = process_video_metadata(video_meta_list, query, video_base_url)
        if items:
            save_to_parquet_thread_safe(pd.DataFrame(items), file_path_parquet, lock)
            return {
                "query": query,
                "success": True,
                "items_count": len(items),
                "error": None,
            }
        else:
            return {
                "query": query,
                "success": False,
                "items_count": 0,
                "error": "No valid items extracted",
            }

    except Exception as exc:
        return {"query": query, "success": False, "items_count": 0, "error": str(exc)}


def collect_and_save_video_metadata_concurrent(
    queries: list[str],
    limit: int,
    sleep: tuple[int, int],
    sp_filter: str,
    results_type: str,
    proxies: dict,
    video_base_url: str,
    file_path_parquet: str | Path,
    max_workers: int | None = None,
) -> list[dict]:
    """Collect video metadata for multiple queries concurrently and save results to a parquet file."""
    if not queries:
        logger.warning("No queries provided")
        return []

    logger.info(f"Starting {len(queries)} queries (workers={max_workers})")

    results = []
    lock = threading.Lock()
    processed_count = 0
    total_queries = len(queries)

    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="query-worker"
    ) as executor:
        future_to_query = {
            executor.submit(
                process_single_query,
                query,
                limit,
                sleep,
                sp_filter,
                results_type,
                proxies,
                video_base_url,
                file_path_parquet,
                lock,
            ): query
            for query in queries
        }

        for future in tqdm(
            as_completed(future_to_query),
            total=len(future_to_query),
            desc="Processing queries",
        ):
            query = future_to_query[future]
            try:
                result = future.result()
                results.append(result)
                processed_count += 1

            except Exception as exc:
                logger.error(f"Exception '{query}': {exc}", exc_info=True)
                results.append(
                    {
                        "query": query,
                        "success": False,
                        "items_count": 0,
                        "error": str(exc),
                    }
                )
                processed_count += 1

    # Summary
    successful_queries = sum(1 for r in results if r["success"])
    total_items = sum(r["items_count"] for r in results)

    logger.info("Finished:")
    logger.info(f"  Processed: {processed_count}/{total_queries}")
    logger.info(f"  Successful: {successful_queries}")
    logger.info(f"  Total items: {total_items}")

    return results
