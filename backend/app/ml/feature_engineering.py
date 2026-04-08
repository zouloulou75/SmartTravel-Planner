from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.ml.constants import REGION_TO_STATE, TIER_LABELS, TRAVEL_MODE_MAPPING, WEATHER_MAPPING


def load_interactions(path: Path, sample_rows: int) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Interaction dataset not found: {path}")
    return pd.read_csv(path, sep="\t", nrows=sample_rows)


def _parse_timestamp_column(frame: pd.DataFrame) -> pd.Series:
    numeric = pd.to_numeric(frame["timestamp"], errors="coerce")
    parsed_ms = pd.to_datetime(numeric, unit="ms", errors="coerce")
    if parsed_ms.notna().any():
        return parsed_ms
    return pd.to_datetime(numeric, unit="s", errors="coerce")


def _assign_region_tier(series: pd.Series) -> pd.Series:
    unique_values = series.dropna().nunique()
    if unique_values <= 1:
        return pd.Series(["Mid-size City"] * len(series), index=series.index)
    bins = min(unique_values, len(TIER_LABELS))
    labels = TIER_LABELS[:bins]
    return pd.qcut(series, q=bins, labels=labels, duplicates="drop").astype(str)


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df = df.drop(columns=["via_poi_id"], errors="ignore")
    df["timestamp"] = _parse_timestamp_column(df)
    df["month"] = df["timestamp"].dt.month.fillna(1).astype(int)
    df["hour"] = df["timestamp"].dt.hour.fillna(12).astype(int)
    df["day_of_week"] = df["timestamp"].dt.dayofweek.fillna(0).astype(int)

    df["weather_label"] = df["weather"].map(WEATHER_MAPPING).fillna("Unknown")
    df["travel_mode_label"] = df["travel_mode"].map(TRAVEL_MODE_MAPPING).fillna("unknown")

    region_freq = df["administrative_region_id"].value_counts()
    df["region_freq"] = (
        df["administrative_region_id"].map(region_freq).fillna(1).astype(int)
    )
    df["region_tier"] = _assign_region_tier(df["region_freq"])

    mapping_df = (
        pd.DataFrame.from_dict(
            REGION_TO_STATE,
            orient="index",
            columns=["state_name", "state_abbr", "census_division"],
        )
        .reset_index()
        .rename(columns={"index": "administrative_region_id"})
    )
    df = df.merge(mapping_df, on="administrative_region_id", how="left")
    df["census_division"] = df["census_division"].fillna("Unknown")

    poi_freq = df["poi_id"].value_counts()
    df["poi_freq"] = df["poi_id"].map(poi_freq).fillna(1).astype(int)
    return df


def build_region_stats(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["census_division", "region_tier"], dropna=False)["region_freq"]
        .agg(region_freq_median="median", sample_count="count")
        .reset_index()
    )


def build_poi_stats(df: pd.DataFrame, candidate_pool_size: int) -> pd.DataFrame:
    poi_freq = df["poi_id"].value_counts().head(candidate_pool_size).reset_index()
    poi_freq.columns = ["poi_id", "poi_freq"]
    poi_freq["popularity_rank"] = range(1, len(poi_freq) + 1)
    max_freq = float(poi_freq["poi_freq"].max() or 1)
    poi_freq["relative_score"] = poi_freq["poi_freq"] / max_freq

    region_cols = [
        "poi_id",
        "administrative_region_id",
        "state_name",
        "state_abbr",
        "census_division",
        "region_tier",
    ]
    dominant_regions = (
        df[region_cols]
        .groupby(region_cols, dropna=False)
        .size()
        .reset_index(name="support")
        .sort_values(["poi_id", "support"], ascending=[True, False])
        .drop_duplicates(subset=["poi_id"])
        .drop(columns=["support"])
    )
    merged = poi_freq.merge(dominant_regions, on="poi_id", how="left")
    return merged.where(pd.notna(merged), None)
