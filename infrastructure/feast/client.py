"""Feast client wrapper."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd


class FeastClient:
    """Client for interacting with Feast feature store."""

    def __init__(
        self,
        online_store: str = "redis://localhost:6379",
        offline_store: Optional[str] = None
    ):
        """
        Initialize Feast client.

        Args:
            online_store: Online store connection string
            offline_store: Offline store connection string
        """
        self.online_store = online_store
        self.offline_store = offline_store
        # NOTE: Actual Feast FeatureStore initialization deferred to Plan 3

    def get_online_features(
        self,
        features: List[str],
        entity_rows: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Get features from online store.

        Stub for Plan 3.
        """
        raise NotImplementedError("get_online_features will be implemented in Plan 3")

    def get_historical_features(
        self,
        entity_df: pd.DataFrame,
        features: List[str]
    ) -> pd.DataFrame:
        """
        Get features from offline store.

        Stub for Plan 3.
        """
        raise NotImplementedError("get_historical_features will be implemented in Plan 3")
