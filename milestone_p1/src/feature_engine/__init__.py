"""Feature engineering pipeline — production-grade Python rewrite.

This package replaces a Spark-based feature engineering pipeline
with pure Python, demonstrating:
  - Full type annotations (mypy strict)
  - Protocol-based dependency injection
  - pytest with mock data sources (via Protocol conformance)
  - Generator-based streaming for memory efficiency
"""

from feature_engine.pipeline import FeaturePipeline
from feature_engine.transforms import (
    build_feature_vector,
    compute_windowed_features,
    encode_categorical,
    stream_events_in_batches,
)
from feature_engine.types import (
    EventSource,
    FeatureVector,
    ProfileSource,
    RawEvent,
    UserProfile,
    WindowedFeature,
)

__all__ = [
    "FeaturePipeline",
    "EventSource",
    "ProfileSource",
    "RawEvent",
    "UserProfile",
    "WindowedFeature",
    "FeatureVector",
    "compute_windowed_features",
    "build_feature_vector",
    "encode_categorical",
    "stream_events_in_batches",
]
