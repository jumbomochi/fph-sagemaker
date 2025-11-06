"""Simple data processing helpers (placeholder)
"""
import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(path)


class DataProcessor:
    """Example data processor for cleaning and feature engineering."""

    def __init__(self):
        pass

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # placeholder logic
        return df.copy()
