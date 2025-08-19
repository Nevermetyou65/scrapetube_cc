"""Creative Commons functionality for scrapetube."""

from .extractor import (
    collect_video_metadata,
    collect_video_metadata_concurrent,
)
from .license import (
    YtDlpLoguruLogger,
    check_video_licenses_concurrent,
    YoutubeUrl,
    NO_LICENSE,
)
from .subtitle import (
    fetch_video_transcripts_concurrent,
)
from .text import (
    convert_subtitles_to_text,
    export_dataframe_to_jsonl,
    TEXT_JSON_LINES,
)

__all__ = [
    # From extractor
    "collect_video_metadata",
    "collect_video_metadata_concurrent",
    # From license
    "YtDlpLoguruLogger",
    "check_video_licenses_concurrent",
    "YoutubeUrl",
    "NO_LICENSE",
    # From subtitle
    "fetch_video_transcripts_concurrent",
    # From text
    "convert_subtitles_to_text",
    "export_dataframe_to_jsonl",
    "TEXT_JSON_LINES",
]
