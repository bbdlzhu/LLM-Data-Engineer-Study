"""Type definitions for the feature engineering pipeline.

In Spark, you'd define schemas with StructType/StructField.
In production Python, we use TypedDict for row-level contracts
and Protocol for abstract interfaces (like Java interfaces).
"""

from typing import Protocol, TypedDict


class RawEvent(TypedDict):
    """A single user behavior event.

    Analogous to a Spark DataFrame row with schema:
      user_id: LongType, event_type: StringType, timestamp: TimestampType, ...
    """

    user_id: str
    event_type: str  # "click", "view", "purchase", "add_to_cart"
    item_id: str
    timestamp: str  # ISO 8601
    value: float  # e.g., purchase amount, or 0 for non-purchase events


class UserProfile(TypedDict):
    """User demographic/profile data.

    Analogous to a dimension table in a star schema.
    """

    user_id: str
    age_group: str  # "18-24", "25-34", "35-44", "45+"
    gender: str
    city_tier: str  # "T1", "T2", "T3"
    registered_at: str  # ISO 8601


class WindowedFeature(TypedDict):
    """Computed window-aggregated features for a single user at a reference date."""

    user_id: str
    reference_date: str
    click_count_7d: int
    click_count_30d: int
    purchase_count_7d: int
    purchase_count_30d: int
    total_spend_7d: float
    total_spend_30d: float
    distinct_items_7d: int
    distinct_items_30d: int


class FeatureVector(TypedDict):
    """Final output: one feature vector per user per reference date.

    This is what the downstream ML model consumes.
    """

    user_id: str
    reference_date: str
    # Raw window features
    click_count_7d: int
    click_count_30d: int
    purchase_count_7d: int
    purchase_count_30d: int
    total_spend_7d: float
    total_spend_30d: float
    distinct_items_7d: int
    distinct_items_30d: int
    # Derived features
    click_growth_7d_to_30d: float
    spend_growth_7d_to_30d: float
    # Encoded categorical features
    age_group_encoded: int
    city_tier_encoded: int
    # Target (for supervised learning)
    label: int  # 1 if purchase within next 7 days, else 0


class EventSource(Protocol):
    """Abstract data source for raw events.

    Protocol classes are Python's answer to Java interfaces.
    They enable dependency injection for testing — in tests we
    inject a mock source instead of hitting a real database.

    Using Protocol (structural subtyping) rather than ABC (nominal subtyping)
    means any object with these methods satisfies the contract — no explicit
    inheritance needed. This is more Pythonic.
    """

    def fetch_events(self, start_date: str, end_date: str) -> list[RawEvent]:
        """Retrieve events in [start_date, end_date)."""
        ...

    def fetch_distinct_user_ids(self, start_date: str, end_date: str) -> list[str]:
        """Get all user_ids that had activity in the date range."""
        ...


class ProfileSource(Protocol):
    """Abstract data source for user profiles."""

    def fetch_profiles(self, user_ids: list[str]) -> list[UserProfile]:
        """Retrieve profiles for the given user IDs."""
        ...
