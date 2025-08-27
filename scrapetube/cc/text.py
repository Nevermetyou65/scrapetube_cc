import re
import polars as pl
from pythainlp.util import normalize
from scrapetube.utils.config import get_timestamp_string, DATA_DIR

pl.Config.set_tbl_width_chars(100)
pl.Config.set_fmt_str_lengths(100)

PAT1 = re.compile(r"([ก-๙])([a-zA-Z0-9])")
PAT2 = re.compile(r"([a-zA-Z0-9])([ก-๙])")

TEXT_JSON_LINES = DATA_DIR / f"text_{get_timestamp_string()}.jsonl"


def _insert_space_thai_english(text: str) -> str:
    """Add space between Thai characters and English characters"""
    text = PAT1.sub(r"\1 \2", text)
    text = PAT2.sub(r"\1 \2", text)
    return text


def _normalize_thai_text(text: str) -> str:
    """Cleans and normalizes a string of Thai text."""
    text = _insert_space_thai_english(text)
    text = normalize(text)
    return text


def convert_subtitles_to_text(df: pl.DataFrame, max_gap: int = 1) -> pl.DataFrame:
    """Processes subtitle data in a Polars DataFrame."""
    return df.with_columns(
        pl.col("subtitles_json")
        .list.eval(
            (pl.element().struct.field("text"))
            + (
                pl.when(
                    pl.element().struct.field("start").shift(-1)
                    - pl.element().struct.field("end")
                    >= max_gap
                )
                .then(pl.lit("\n"))
                .otherwise(pl.lit(""))
            )
        )
        .list.join("")
        .alias("text")
    ).with_columns(
        pl.col("text").map_elements(
            lambda x: _normalize_thai_text(x),
            return_dtype=pl.Utf8,
        )
    )


def export_dataframe_to_jsonl(df: pl.DataFrame) -> list[dict]:
    """
    Transforms a DataFrame into a list of dictionaries with a specific structure.

    Args:
        df: The input Polars DataFrame.

    Returns:
        A list of dictionaries.
    """
    df_with_id = df.with_row_index(name="id", offset=1).with_columns(
        pl.col("id").cast(pl.Utf8)
    )

    result_df = df_with_id.select(
        pl.col("id"),
        pl.col("text"),
        pl.lit("youtube").alias("source"),
        pl.struct(
            [
                pl.lit("Creative Commons Attribution license (reuse allowed)").alias(
                    "license"
                ),
                pl.col("at_channel").alias("channel_name"),
                pl.col("title"),
                pl.col("video_url"),
                pl.col("is_generated").cast(pl.Utf8).alias("is_subtitle_generated"),
            ]
        ).alias("metadata"),
    )
    result_df.write_ndjson(TEXT_JSON_LINES)
