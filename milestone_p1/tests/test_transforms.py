"""Tests for feature_engine.transforms.

Demonstrates pytest patterns:
  - fixtures for test data (in conftest.py)
  - parametrize for multiple input/output pairs
  - Edge case coverage (empty inputs, missing data)
"""

from datetime import datetime, timedelta

import pytest

from feature_engine.transforms import (
    AGE_GROUP_ENCODING,
    CITY_TIER_ENCODING,
    _safe_ratio,
    build_feature_vector,
    compute_windowed_features,
    encode_categorical,
    stream_events_in_batches,
)
from feature_engine.types import RawEvent, UserProfile, WindowedFeature


class TestComputeWindowedFeatures:
    """Tests for the core window aggregation function.

    This is the computational heart of the pipeline — analogous to testing
    your Spark groupBy + agg logic, but all in-process with no cluster.
    """

    def test_heavy_user_features(
        self,
        sample_events: list[RawEvent],
        reference_date: str,
    ) -> None:
        """u1 has 5 clicks + 2 purchases in last 7 days."""
        result = compute_windowed_features(
            sample_events, ["u1"], reference_date
        )

        assert "u1" in result
        f = result["u1"]
        assert f["click_count_7d"] == 5
        assert f["purchase_count_7d"] == 2
        assert f["total_spend_7d"] == pytest.approx(248.0)
        # Distinct items tracked from purchase events only: item_0 + item_1 = 2
        assert f["distinct_items_7d"] == 2

    def test_lapsed_user_only_in_long_window(
        self,
        sample_events: list[RawEvent],
        reference_date: str,
    ) -> None:
        """u3 has activity 8-10 days ago: in 30d window but not 7d."""
        result = compute_windowed_features(
            sample_events, ["u3"], reference_date
        )

        f = result["u3"]
        assert f["click_count_7d"] == 0
        assert f["purchase_count_7d"] == 0
        assert f["total_spend_7d"] == 0.0
        assert f["click_count_30d"] == 2
        assert f["purchase_count_30d"] == 1
        assert f["total_spend_30d"] == pytest.approx(199.0)

    def test_all_users_returned(self, sample_events: list[RawEvent], reference_date: str) -> None:
        """Every requested user gets a result entry."""
        result = compute_windowed_features(
            sample_events, ["u1", "u2", "u3"], reference_date
        )
        assert set(result.keys()) == {"u1", "u2", "u3"}

    def test_empty_events(self, reference_date: str) -> None:
        """No events → all zeros."""
        result = compute_windowed_features([], ["u1"], reference_date)
        f = result["u1"]
        assert f["click_count_7d"] == 0
        assert f["total_spend_30d"] == 0.0

    def test_empty_user_list(self, sample_events: list[RawEvent], reference_date: str) -> None:
        """No users requested → empty result."""
        result = compute_windowed_features(sample_events, [], reference_date)
        assert result == {}

    def test_unknown_user_not_in_result(
        self, sample_events: list[RawEvent], reference_date: str
    ) -> None:
        """Requesting a user with no events still returns zeros."""
        result = compute_windowed_features(sample_events, ["u999"], reference_date)
        f = result["u999"]
        assert f["click_count_7d"] == 0

    def test_event_outside_windows_is_ignored(
        self, reference_date: str
    ) -> None:
        """Events older than 30 days should not be counted."""
        ref_dt = datetime.fromisoformat(reference_date)
        old_event = RawEvent(
            user_id="u1",
            event_type="click",
            item_id="ancient",
            timestamp=(ref_dt - timedelta(days=60)).isoformat(),
            value=0.0,
        )
        result = compute_windowed_features([old_event], ["u1"], reference_date)
        assert result["u1"]["click_count_30d"] == 0


class TestEncodeCategorical:
    def test_known_category(self) -> None:
        assert encode_categorical("25-34", AGE_GROUP_ENCODING) == 1

    def test_unknown_category_returns_default(self) -> None:
        assert encode_categorical("unknown_bucket", AGE_GROUP_ENCODING) == -1

    def test_custom_default(self) -> None:
        assert encode_categorical("unknown", CITY_TIER_ENCODING, default=99) == 99

    def test_empty_mapping_raises(self) -> None:
        with pytest.raises(ValueError, match="不能为空"):
            encode_categorical("x", {})


class TestBuildFeatureVector:
    def test_basic_assembly(self, reference_date: str) -> None:
        """Happy path: windowed features + profile → FeatureVector."""
        wf = WindowedFeature(
            user_id="u1",
            reference_date=reference_date,
            click_count_7d=10,
            click_count_30d=30,
            purchase_count_7d=2,
            purchase_count_30d=8,
            total_spend_7d=100.0,
            total_spend_30d=500.0,
            distinct_items_7d=5,
            distinct_items_30d=15,
        )
        profile = UserProfile(
            user_id="u1",
            age_group="25-34",
            gender="M",
            city_tier="T1",
            registered_at="2023-01-01",
        )

        fv = build_feature_vector(wf, profile)

        assert fv["user_id"] == "u1"
        assert fv["click_growth_7d_to_30d"] == pytest.approx(10.0 / 30.0)
        assert fv["spend_growth_7d_to_30d"] == pytest.approx(100.0 / 500.0)
        assert fv["age_group_encoded"] == 1  # "25-34"
        assert fv["city_tier_encoded"] == 0  # "T1"
        assert fv["label"] == 0  # No lookahead events → label=0

    def test_label_positive_with_purchase_lookahead(self, reference_date: str) -> None:
        """When lookahead contains a purchase, label=1."""
        wf = WindowedFeature(
            user_id="u1",
            reference_date=reference_date,
            click_count_7d=0,
            click_count_30d=0,
            purchase_count_7d=0,
            purchase_count_30d=0,
            total_spend_7d=0.0,
            total_spend_30d=0.0,
            distinct_items_7d=0,
            distinct_items_30d=0,
        )
        profile = UserProfile(
            user_id="u1",
            age_group="18-24",
            gender="F",
            city_tier="T2",
            registered_at="2023-01-01",
        )
        ref_dt = datetime.fromisoformat(reference_date)
        lookahead = [
            RawEvent(
                user_id="u1",
                event_type="purchase",
                item_id="x",
                timestamp=(ref_dt + timedelta(days=1)).isoformat(),
                value=50.0,
            )
        ]
        fv = build_feature_vector(wf, profile, label_lookahead_events=lookahead)
        assert fv["label"] == 1

    def test_label_zero_when_only_clicks_in_lookahead(self, reference_date: str) -> None:
        """Only clicks in lookahead → label=0 (no purchase)."""
        wf = WindowedFeature(
            user_id="u2",
            reference_date=reference_date,
            click_count_7d=0,
            click_count_30d=0,
            purchase_count_7d=0,
            purchase_count_30d=0,
            total_spend_7d=0.0,
            total_spend_30d=0.0,
            distinct_items_7d=0,
            distinct_items_30d=0,
        )
        profile = UserProfile(
            user_id="u2",
            age_group="18-24",
            gender="F",
            city_tier="T2",
            registered_at="2023-01-01",
        )
        ref_dt = datetime.fromisoformat(reference_date)
        lookahead = [
            RawEvent(
                user_id="u2",
                event_type="click",
                item_id="y",
                timestamp=(ref_dt + timedelta(days=1)).isoformat(),
                value=0.0,
            )
        ]
        fv = build_feature_vector(wf, profile, label_lookahead_events=lookahead)
        assert fv["label"] == 0


class TestSafeRatio:
    def test_normal_division(self) -> None:
        assert _safe_ratio(10, 20) == 0.5

    def test_zero_denominator(self) -> None:
        assert _safe_ratio(10, 0) == 0.0

    def test_zero_numerator(self) -> None:
        assert _safe_ratio(0, 10) == 0.0

    def test_float_inputs(self) -> None:
        assert _safe_ratio(1.5, 3.0) == 0.5


class TestStreamEventsInBatches:
    def test_exact_batches(self) -> None:
        events = [
            RawEvent(
                user_id=str(i),
                event_type="click",
                item_id="x",
                timestamp="2024-01-01T00:00:00",
                value=0.0,
            )
            for i in range(100)
        ]
        batches = list(stream_events_in_batches(events, batch_size=25))
        assert len(batches) == 4
        assert all(len(b) == 25 for b in batches)

    def test_partial_final_batch(self) -> None:
        events = [
            RawEvent(
                user_id=str(i),
                event_type="click",
                item_id="x",
                timestamp="2024-01-01T00:00:00",
                value=0.0,
            )
            for i in range(10)
        ]
        batches = list(stream_events_in_batches(events, batch_size=3))
        assert len(batches) == 4  # 3+3+3+1
        assert len(batches[-1]) == 1

    def test_empty_input(self) -> None:
        assert list(stream_events_in_batches([], batch_size=100)) == []
