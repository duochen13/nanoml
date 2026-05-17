from nanoml.features import Feature, FeatureGroup


# User features
user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[
        Feature("total_ratings", "int"),        # Total movies rated
        Feature("avg_rating", "float"),         # Average rating given
        Feature("rating_stddev", "float"),      # Rating variance
        Feature("favorite_genre", "string"),    # Most watched genre
    ],
    source="kafka://user_events"
)

# Movie features
movie_features = FeatureGroup(
    name="movie_features",
    entity="movie_id",
    features=[
        Feature("genres", "string"),            # Pipe-separated genres
        Feature("release_year", "int"),         # Extracted from title
        Feature("avg_rating", "float"),         # Average rating received
        Feature("rating_count", "int"),         # Number of ratings
    ],
    source="kafka://movie_events"
)

# User-movie interaction features
interaction_features = FeatureGroup(
    name="interaction_features",
    entity="user_id",
    features=[
        Feature("last_rating_timestamp", "int"),   # Most recent rating
        Feature("days_since_last_rating", "int"),  # Recency
        Feature("rated_genres", "string"),         # Genres user has rated
    ],
    source="kafka://rating_events"
)
