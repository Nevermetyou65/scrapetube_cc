"""Wrapper for scrapetube to extract YouTube video metadata."""

import json
from pathlib import Path

import pandas as pd
from loguru import logger

from scrapetube.scrapetube import get_search_creative_commons


def save_to_parquet(df: pd.DataFrame, file_path_parquet: str | Path) -> None:
    """Save a DataFrame to a parquet file, appending if possible."""
    try:
        df.to_parquet(file_path_parquet, engine="fastparquet", index=False, append=True)
    except FileNotFoundError:
        df.to_parquet(file_path_parquet, engine="fastparquet", index=False)
    except Exception as e:
        logger.error(f"Error saving to parquet {file_path_parquet}: {e}")


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
        logger.debug(f"Error extracting metadata: {e}")
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
        logger.error(f"Direct request failed for '{query}': {e}")
        return []


def process_video_metadata(
    video_meta_list: list[dict],
    query: str,
    video_base_url: str,
    limit: int,
) -> list[dict]:
    """Process a list of video metadata dictionaries and extract relevant fields."""
    items = []
    successful_extractions = 0
    logger.info(f"Processing {len(video_meta_list)} for '{query}'")
    for video_meta in video_meta_list[:limit]:
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
        logger.info(f"Found {len(video_meta_list)} results for '{query}'")

    else:
        logger.warning(f"No results for '{query}'")
        return

    items = process_video_metadata(video_meta_list, query, video_base_url, limit)

    if items:
        save_to_parquet(pd.DataFrame(items), file_path_parquet)
    else:
        logger.warning(f"No valid items for '{query}'")
