"""Shared fixtures for feature_engine tests.

Fixtures in pytest are like Spark's test data setup:
you define reusable test inputs once and inject them
into any test that needs them.
"""

from datetime import datetime, timedelta

import pytest

from feature_engine.types import RawEvent, UserProfile


@pytest.fixture
def reference_date() -> str:
    """The "as of" date for feature computation."""
    return "2024-01-15"


@pytest.fixture
def sample_profiles() -> list[UserProfile]:
    """Three users across different demographics."""
    return [
        UserProfile(
            user_id="u1",
            age_group="25-34",
            gender="M",
            city_tier="T1",
            registered_at="2023-06-01",
        ),
        UserProfile(
            user_id="u2",
            age_group="18-24",
            gender="F",
            city_tier="T2",
            registered_at="2023-08-15",
        ),
        UserProfile(
            user_id="u3",
            age_group="35-44",
            gender="M",
            city_tier="T3",
            registered_at="2022-01-10",
        ),
    ]


@pytest.fixture
def sample_events(reference_date: str) -> list[RawEvent]:
    """Generate deterministic test events for 3 users over 35 days.

    Covers: clicks, purchases, multi-item views, and a user (u3) with
    activity only outside the short window.
    """
    ref_dt = datetime.fromisoformat(reference_date)
    events: list[RawEvent] = []

    # u1: heavy user — 5 clicks and 2 purchases in last 7 days
    for i in range(5):
        events.append(
            RawEvent(
                user_id="u1",
                event_type="click",
                item_id=f"item_{i}",
                timestamp=(ref_dt - timedelta(days=i)).isoformat(),
                value=0.0,
            )
        )
    events.append(
        RawEvent(
            user_id="u1",
            event_type="purchase",
            item_id="item_0",
            timestamp=(ref_dt - timedelta(days=3)).isoformat(),
            value=99.0,
        )
    )
    events.append(
        RawEvent(
            user_id="u1",
            event_type="purchase",
            item_id="item_1",
            timestamp=(ref_dt - timedelta(days=1)).isoformat(),
            value=149.0,
        )
    )

    # u2: moderate user — 3 clicks, 1 purchase in last 7 days
    for i in range(3):
        events.append(
            RawEvent(
                user_id="u2",
                event_type="click",
                item_id=f"item_{i + 10}",
                timestamp=(ref_dt - timedelta(days=i + 1)).isoformat(),
                value=0.0,
            )
        )
    events.append(
        RawEvent(
            user_id="u2",
            event_type="purchase",
            item_id="item_10",
            timestamp=(ref_dt - timedelta(days=2)).isoformat(),
            value=49.0,
        )
    )

    # u3: lapsed user — only activity 8-30 days ago (long window only)
    for i in range(2):
        events.append(
            RawEvent(
                user_id="u3",
                event_type="click",
                item_id=f"item_{i + 20}",
                timestamp=(ref_dt - timedelta(days=8 + i)).isoformat(),
                value=0.0,
            )
        )
    events.append(
        RawEvent(
            user_id="u3",
            event_type="purchase",
            item_id="item_20",
            timestamp=(ref_dt - timedelta(days=10)).isoformat(),
            value=199.0,
        )
    )

    return events


@pytest.fixture
def sample_events_with_lookahead(reference_date: str) -> list[RawEvent]:
    """Events including a 7-day lookahead window for label computation."""
    ref_dt = datetime.fromisoformat(reference_date)

    events: list[RawEvent] = []

    # u1: click and purchase in lookahead → label=1
    events.append(
        RawEvent(
            user_id="u1",
            event_type="click",
            item_id="item_99",
            timestamp=(ref_dt + timedelta(days=1)).isoformat(),
            value=0.0,
        )
    )
    events.append(
        RawEvent(
            user_id="u1",
            event_type="purchase",
            item_id="item_99",
            timestamp=(ref_dt + timedelta(days=3)).isoformat(),
            value=299.0,
        )
    )

    # u2: clicks in lookahead but no purchase → label=0
    events.append(
        RawEvent(
            user_id="u2",
            event_type="click",
            item_id="item_88",
            timestamp=(ref_dt + timedelta(days=2)).isoformat(),
            value=0.0,
        )
    )

    return events
