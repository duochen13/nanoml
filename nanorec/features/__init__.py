"""Feature definitions for NanoRec."""

from dataclasses import dataclass
from typing import List


@dataclass
class Feature:
    """A single feature in a feature group.

    Attributes:
        name: Feature name
        dtype: Data type (int, float, string, boolean)
    """
    name: str
    dtype: str


@dataclass
class FeatureGroup:
    """A group of related features.

    Attributes:
        name: Feature group name
        entity: Entity ID column (e.g., "user_id", "movie_id")
        features: List of features in this group
        source: Data source (e.g., "kafka://topic_name")
    """
    name: str
    entity: str
    features: List[Feature]
    source: str
