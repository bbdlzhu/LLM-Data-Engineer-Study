"""Feature computation module.

This is the core of the pipeline — where raw events and profiles
are transformed into feature vectors. This mirrors what you'd do
with Spark's groupBy, agg, window functions, and StringIndexer.

Key Python production practices demonstrated:
  - TypeVar/Generic for reusable utilities
  - Generator functions for memory-efficient streaming
  - Explicit error handling at data boundaries
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Iterator

from feature_engine.types import (
    FeatureVector,
    RawEvent,
    UserProfile,
    WindowedFeature,
)


def compute_windowed_features(
    events: list[RawEvent],
    user_ids: list[str],
    reference_date: str,
    *,
    short_window_days: int = 7,
    long_window_days: int = 30,
) -> dict[str, WindowedFeature]:
    """Compute rolling-window aggregations for each user.

    This replaces what in Spark would be:
      df.groupBy("user_id")
        .agg(
            sum(when(col("event_type")=="click",1)
                .when(col("timestamp")>=window_start,1)
                .otherwise(0)).alias("click_count_7d"),
            ...
        )

    The Spark version is declarative (describe what you want).
    The pure Python version is imperative — but with type safety
    the compiler catches schema mismatches at dev time rather
    than runtime.

    Args:
        events: All raw events in the window period.
        user_ids: Which users to compute features for.
        reference_date: The "as of" date for computing lookback windows.
        short_window_days: Short lookback (default 7 days).
        long_window_days: Long lookback (default 30 days).

    Returns:
        Dict mapping user_id -> WindowedFeature.
    """
    ref_date = datetime.fromisoformat(reference_date)
    short_start = ref_date - timedelta(days=short_window_days)
    long_start = ref_date - timedelta(days=long_window_days)

    # Initialize accumulators for each user
    # Using defaultdict for clean accumulation — equivalent to Spark's
    # groupBy + agg pattern but explicit about initial values.
    accumulators: dict[str, dict[str, float | int | set[str]]] = {
        uid: {
            "click_count_7d": 0,
            "click_count_30d": 0,
            "purchase_count_7d": 0,
            "purchase_count_30d": 0,
            "total_spend_7d": 0.0,
            "total_spend_30d": 0.0,
            "distinct_items_7d": set(),
            "distinct_items_30d": set(),
        }
        for uid in user_ids
    }

    user_id_set = frozenset(user_ids)

    for event in events:
        uid = event["user_id"]
        if uid not in user_id_set:
            continue

        ts = datetime.fromisoformat(event["timestamp"])
        acc = accumulators[uid]

        in_short = ts >= short_start
        in_long = ts >= long_start

        if event["event_type"] == "click":
            if in_short:
                c7 = acc["click_count_7d"]
                assert isinstance(c7, int)
                acc["click_count_7d"] = c7 + 1
            if in_long:
                c30 = acc["click_count_30d"]
                assert isinstance(c30, int)
                acc["click_count_30d"] = c30 + 1

        elif event["event_type"] == "purchase":
            if in_short:
                p7 = acc["purchase_count_7d"]
                s7 = acc["total_spend_7d"]
                assert isinstance(p7, int)
                assert isinstance(s7, float)
                acc["purchase_count_7d"] = p7 + 1
                acc["total_spend_7d"] = s7 + event["value"]
            if in_long:
                p30 = acc["purchase_count_30d"]
                s30 = acc["total_spend_30d"]
                assert isinstance(p30, int)
                assert isinstance(s30, float)
                acc["purchase_count_30d"] = p30 + 1
                acc["total_spend_30d"] = s30 + event["value"]

            # Track distinct items (use set, then convert to count)
            if in_short:
                di7 = acc["distinct_items_7d"]
                assert isinstance(di7, set)
                di7.add(event["item_id"])
            if in_long:
                di30 = acc["distinct_items_30d"]
                assert isinstance(di30, set)
                di30.add(event["item_id"])

    # Build output — converting sets to counts
    result: dict[str, WindowedFeature] = {}
    for uid, acc in accumulators.items():
        c7 = acc["click_count_7d"]
        c30 = acc["click_count_30d"]
        p7 = acc["purchase_count_7d"]
        p30 = acc["purchase_count_30d"]
        s7 = acc["total_spend_7d"]
        s30 = acc["total_spend_30d"]
        di7 = acc["distinct_items_7d"]
        di30 = acc["distinct_items_30d"]
        assert isinstance(c7, int)
        assert isinstance(c30, int)
        assert isinstance(p7, int)
        assert isinstance(p30, int)
        assert isinstance(s7, float)
        assert isinstance(s30, float)
        assert isinstance(di7, set)
        assert isinstance(di30, set)

        result[uid] = WindowedFeature(
            user_id=uid,
            reference_date=reference_date,
            click_count_7d=c7,
            click_count_30d=c30,
            purchase_count_7d=p7,
            purchase_count_30d=p30,
            total_spend_7d=s7,
            total_spend_30d=s30,
            distinct_items_7d=len(di7),
            distinct_items_30d=len(di30),
        )

    return result


def stream_events_in_batches(
    events: list[RawEvent],
    batch_size: int = 10000,
) -> Iterator[list[RawEvent]]:
    """Stream events in fixed-size batches.

    Generator function — yields control back to the caller after each batch.
    In Spark this would be handled by the execution engine automatically;
    in pure Python we manage memory explicitly.

    Use case: when events don't fit in memory, stream from disk/S3
    and process in chunks. This generator pattern is a Pythonic way
    to implement backpressure-aware pipelines.
    """
    for i in range(0, len(events), batch_size):
        yield events[i : i + batch_size]


def encode_categorical(
    value: str,
    mapping: dict[str, int],
    *,
    default: int = -1,
) -> int:
    """Encode a categorical string value to integer.

    Equivalent to Spark's StringIndexer + one-hot encoding prep.
    Returns default (-1) for unseen categories — in production you'd
    log a warning and potentially route to a dead-letter queue.

    Raises:
        ValueError: If the mapping is empty.
    """
    if not mapping:
        raise ValueError("encoding mapping must not be empty")
    return mapping.get(value, default)


# Pre-defined encoding maps — in production these come from
# a configuration file or a trained encoder artifact.
AGE_GROUP_ENCODING: dict[str, int] = {
    "18-24": 0,
    "25-34": 1,
    "35-44": 2,
    "45+": 3,
}

CITY_TIER_ENCODING: dict[str, int] = {
    "T1": 0,
    "T2": 1,
    "T3": 2,
}


def build_feature_vector(
    windowed: WindowedFeature,
    profile: UserProfile,
    *,
    label_lookahead_events: list[RawEvent] | None = None,
) -> FeatureVector:
    """Assemble the final feature vector from windowed features + profile.

    Combines:
      1. Raw window aggregations (from compute_windowed_features)
      2. Derived features (growth ratios)
      3. Encoded categoricals (from user profile)
      4. Label (from future events, if provided)

    Args:
        windowed: Pre-computed window aggregation.
        profile: User demographic profile.
        label_lookahead_events: Events in the 7-day lookahead window
            for computing the supervised learning label.

    Returns:
        A complete FeatureVector ready for model consumption.
    """
    # Derived features: growth ratios
    # Guard against division by zero — if 30d is 0, growth is 0 (not infinity).
    click_growth = _safe_ratio(windowed["click_count_7d"], windowed["click_count_30d"])
    spend_growth = _safe_ratio(windowed["total_spend_7d"], windowed["total_spend_30d"])

    # Label: did the user make any purchase in the lookahead window?
    label = 0
    if label_lookahead_events:
        label = 1 if any(e["event_type"] == "purchase" for e in label_lookahead_events) else 0

    return FeatureVector(
        user_id=windowed["user_id"],
        reference_date=windowed["reference_date"],
        click_count_7d=windowed["click_count_7d"],
        click_count_30d=windowed["click_count_30d"],
        purchase_count_7d=windowed["purchase_count_7d"],
        purchase_count_30d=windowed["purchase_count_30d"],
        total_spend_7d=windowed["total_spend_7d"],
        total_spend_30d=windowed["total_spend_30d"],
        distinct_items_7d=windowed["distinct_items_7d"],
        distinct_items_30d=windowed["distinct_items_30d"],
        click_growth_7d_to_30d=click_growth,
        spend_growth_7d_to_30d=spend_growth,
        age_group_encoded=encode_categorical(profile["age_group"], AGE_GROUP_ENCODING),
        city_tier_encoded=encode_categorical(profile["city_tier"], CITY_TIER_ENCODING),
        label=label,
    )


def _safe_ratio(numerator: int | float, denominator: int | float) -> float:
    """Compute numerator/denominator, returning 0.0 when denominator is 0."""
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)
