"""Integration-style tests for FeaturePipeline.

These tests use mock data sources that conform to the EventSource
and ProfileSource Protocols — demonstrating how Protocol enables
testability without mocking libraries.

In Spark: testing pipelines typically requires a local SparkSession
or a test cluster. With Protocol-based DI, our pipeline tests run
in milliseconds with zero external dependencies.
"""

from datetime import datetime, timedelta

import pytest

from feature_engine.pipeline import FeaturePipeline
from feature_engine.types import EventSource, ProfileSource, RawEvent, UserProfile


class MockEventSource:
    """In-memory event source implementing the EventSource Protocol.

    No inheritance needed — structural subtyping means any class
    with the right method signatures satisfies the Protocol.
    """

    def __init__(self, events: list[RawEvent]) -> None:
        self._events = events

    def fetch_events(self, start_date: str, end_date: str) -> list[RawEvent]:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        return [
            e
            for e in self._events
            if start <= datetime.fromisoformat(e["timestamp"]) < end
        ]

    def fetch_distinct_user_ids(self, start_date: str, end_date: str) -> list[str]:
        events_in_range = self.fetch_events(start_date, end_date)
        return sorted({e["user_id"] for e in events_in_range})


class MockProfileSource:
    """In-memory profile source implementing the ProfileSource Protocol."""

    def __init__(self, profiles: list[UserProfile]) -> None:
        self._profiles = {p["user_id"]: p for p in profiles}

    def fetch_profiles(self, user_ids: list[str]) -> list[UserProfile]:
        return [self._profiles[uid] for uid in user_ids if uid in self._profiles]


def make_event(
    user_id: str,
    event_type: str,
    days_offset: int,
    item_id: str = "x",
    value: float = 0.0,
) -> RawEvent:
    """Helper to create events at a given offset from reference_date."""
    ref = datetime.fromisoformat("2024-01-15")
    return RawEvent(
        user_id=user_id,
        event_type=event_type,
        item_id=item_id,
        timestamp=(ref + timedelta(days=days_offset)).isoformat(),
        value=value,
    )


class TestFeaturePipeline:
    """End-to-end pipeline tests with mock data sources."""

    REFERENCE_DATE = "2024-01-15"

    def test_full_pipeline_single_user(self) -> None:
        """Happy path: one user with events + profile → one feature vector."""
        events = [
            make_event("u1", "click", -5),
            make_event("u1", "click", -3),
            make_event("u1", "purchase", -1, value=99.0),
            # Lookahead: purchase in next 7 days → label=1
            make_event("u1", "purchase", +2, value=50.0),
        ]
        profiles = [
            UserProfile(
                user_id="u1",
                age_group="25-34",
                gender="M",
                city_tier="T1",
                registered_at="2023-01-01",
            )
        ]

        pipeline = FeaturePipeline(
            MockEventSource(events), MockProfileSource(profiles)
        )
        result = pipeline.run(self.REFERENCE_DATE)

        assert len(result) == 1
        fv = result[0]
        assert fv["user_id"] == "u1"
        assert fv["click_count_7d"] == 2
        assert fv["purchase_count_7d"] == 1
        assert fv["total_spend_7d"] == pytest.approx(99.0)
        assert fv["label"] == 1  # Purchase in lookahead

    def test_pipeline_respects_date_boundaries(self) -> None:
        """Events outside the 30-day lookback are excluded."""
        events = [
            make_event("u1", "click", -60),  # Too old: 60 days ago
            make_event("u1", "click", -5),  # Within 30-day window
        ]
        profiles = [
            UserProfile(
                user_id="u1",
                age_group="18-24",
                gender="F",
                city_tier="T2",
                registered_at="2023-01-01",
            )
        ]

        pipeline = FeaturePipeline(
            MockEventSource(events), MockProfileSource(profiles)
        )
        result = pipeline.run(self.REFERENCE_DATE)

        assert len(result) == 1
        # Only the -5 day event should be counted
        # The -60 day event is outside the 30-day lookback
        assert result[0]["click_count_30d"] == 1

    def test_pipeline_no_active_users(self) -> None:
        """When no users have events in the lookback, return empty."""
        events: list[RawEvent] = []
        profiles: list[UserProfile] = []

        pipeline = FeaturePipeline(
            MockEventSource(events), MockProfileSource(profiles)
        )
        result = pipeline.run(self.REFERENCE_DATE)
        assert result == []

    def test_pipeline_user_without_profile_is_skipped(self) -> None:
        """Users with events but no profile are excluded (data quality gap)."""
        events = [
            make_event("u1", "click", -1),
        ]
        profiles: list[UserProfile] = []  # u1 has no profile

        pipeline = FeaturePipeline(
            MockEventSource(events), MockProfileSource(profiles)
        )
        result = pipeline.run(self.REFERENCE_DATE)
        assert result == []  # u1 skipped because no profile

    def test_pipeline_output_is_sorted_by_user_id(self) -> None:
        """Output feature vectors sorted by user_id for deterministic ordering."""
        events = [
            make_event("u3", "click", -1),
            make_event("u1", "click", -1),
            make_event("u2", "click", -1),
        ]
        profiles = [
            UserProfile(
                user_id=uid,
                age_group="25-34",
                gender="M",
                city_tier="T1",
                registered_at="2023-01-01",
            )
            for uid in ["u1", "u2", "u3"]
        ]

        pipeline = FeaturePipeline(
            MockEventSource(events), MockProfileSource(profiles)
        )
        result = pipeline.run(self.REFERENCE_DATE)

        assert [fv["user_id"] for fv in result] == ["u1", "u2", "u3"]

    def test_multiple_users_full_pipeline(self) -> None:
        """Integration test: 3 users with different activity levels."""
        events = [
            # u1: heavy purchaser
            make_event("u1", "click", -5),
            make_event("u1", "click", -4),
            make_event("u1", "purchase", -2, value=200.0),
            make_event("u1", "purchase", +1, value=100.0),  # label=1
            # u2: browser only
            make_event("u2", "click", -3),
            make_event("u2", "click", -1),
            # u3: lapsed
            make_event("u3", "click", -20),
        ]
        profiles = [
            UserProfile(
                user_id=uid,
                age_group="25-34",
                gender="M",
                city_tier="T1",
                registered_at="2023-01-01",
            )
            for uid in ["u1", "u2", "u3"]
        ]

        pipeline = FeaturePipeline(
            MockEventSource(events), MockProfileSource(profiles)
        )
        result = pipeline.run(self.REFERENCE_DATE)

        assert len(result) == 3
        u1 = result[0]
        u2 = result[1]
        u3 = result[2]

        assert u1["label"] == 1
        assert u1["purchase_count_7d"] == 1
        assert u1["total_spend_7d"] == 200.0

        assert u2["label"] == 0
        assert u2["click_count_7d"] == 2
        assert u2["purchase_count_7d"] == 0

        assert u3["label"] == 0
        assert u3["click_count_7d"] == 0  # 20 days ago not in 7d window
        assert u3["click_count_30d"] == 1  # But it is in 30d window
