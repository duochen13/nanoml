import pytest
from features.definitions import user_features, movie_features, interaction_features


def test_user_features_defined():
    """user_features FeatureGroup is properly defined."""
    assert user_features.name == "user_features"
    assert user_features.entity == "user_id"
    assert user_features.source == "kafka://user_events"

    # Should have features
    assert len(user_features.features) >= 3


def test_movie_features_defined():
    """movie_features FeatureGroup is properly defined."""
    assert movie_features.name == "movie_features"
    assert movie_features.entity == "movie_id"
    assert movie_features.source == "kafka://movie_events"

    # Should have features
    assert len(movie_features.features) >= 2


def test_interaction_features_defined():
    """interaction_features FeatureGroup is properly defined."""
    assert interaction_features.name == "interaction_features"
    assert interaction_features.entity == "user_id"
    assert interaction_features.source == "kafka://rating_events"

    # Should track user behavior
    assert len(interaction_features.features) >= 2
