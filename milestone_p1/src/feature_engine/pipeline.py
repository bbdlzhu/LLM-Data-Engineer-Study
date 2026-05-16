"""Pipeline orchestration module.

Coordinates the flow: fetch events → compute windows → join profiles → output features.

In Spark: this is your driver program that chains DataFrame transformations.
In production Python: explicit composition with dependency injection for testability.

Design decision (ADR-001):
  We inject EventSource and ProfileSource via constructor rather than
  importing concrete implementations. This makes the pipeline testable
  without a real database — pass mock sources in tests.
"""

from feature_engine.types import (
    EventSource,
    FeatureVector,
    ProfileSource,
    WindowedFeature,
)
from feature_engine.transforms import build_feature_vector, compute_windowed_features


class FeaturePipeline:
    """Orchestrates the feature engineering process.

    Constructor injection of data sources follows the Dependency Inversion
    Principle: high-level policy (pipeline) doesn't depend on low-level
    details (database connections, file formats).

    Usage:
        pipeline = FeaturePipeline(event_source, profile_source)
        features = pipeline.run(reference_date="2024-01-15")
    """

    def __init__(self, event_source: EventSource, profile_source: ProfileSource) -> None:
        self._events = event_source
        self._profiles = profile_source

    def run(self, reference_date: str) -> list[FeatureVector]:
        """Execute the full feature engineering pipeline.

        Pipeline stages:
          1. Fetch events in the 30-day lookback + 7-day lookahead
          2. Determine active user set
          3. Compute windowed aggregations (7d, 30d)
          4. Fetch user profiles
          5. Join profiles to windowed features
          6. Assemble final feature vectors with labels

        Args:
            reference_date: The "as of" date (ISO 8601). Features are
                computed using lookback windows from this date.

        Returns:
            One FeatureVector per active user, sorted by user_id.
        """
        from datetime import datetime, timedelta

        ref_dt = datetime.fromisoformat(reference_date)

        # Lookback: 30 days before reference date
        lookback_start = (ref_dt - timedelta(days=30)).isoformat()
        # Lookahead: 7 days after reference date (for label computation)
        lookahead_end = (ref_dt + timedelta(days=7)).isoformat()

        # Stage 1: Fetch raw events
        all_events = self._events.fetch_events(lookback_start, lookahead_end)

        # Stage 2: Determine active user set (users with any event in lookback)
        active_user_ids = self._events.fetch_distinct_user_ids(
            lookback_start, reference_date
        )

        if not active_user_ids:
            return []

        # Stage 3: Compute window aggregations
        # Split events into lookback (features) and lookahead (labels)
        lookback_events = [
            e for e in all_events if e["timestamp"] < reference_date
        ]
        lookahead_events = [
            e for e in all_events if e["timestamp"] >= reference_date
        ]

        windowed = compute_windowed_features(
            lookback_events, active_user_ids, reference_date
        )

        # Stage 4: Fetch user profiles
        profiles = self._profiles.fetch_profiles(active_user_ids)
        profile_map = {p["user_id"]: p for p in profiles}

        # Stage 5 & 6: Join + assemble
        result: list[FeatureVector] = []
        for uid in sorted(active_user_ids):
            wf = windowed.get(uid)
            pf = profile_map.get(uid)

            if wf is None:
                continue  # No windowed features for this user (shouldn't happen)
            if pf is None:
                continue  # No profile for this user (data quality issue — log it)

            user_lookahead = [e for e in lookahead_events if e["user_id"] == uid]
            fv = build_feature_vector(wf, pf, label_lookahead_events=user_lookahead)
            result.append(fv)

        return result
