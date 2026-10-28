from __future__ import annotations

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CountryGrouper(BaseEstimator, TransformerMixin):
    def __init__(self, top_n: int = 9, other_label: str = "Other") -> None:
        self.top_n = top_n
        self.other_label = other_label
        self.top_countries_: list[str] = []

    def fit(self, X: pd.DataFrame, y=None) -> "CountryGrouper":
        frame = self._to_frame(X)
        countries = frame["country"].fillna(self.other_label).astype(str).str.strip()
        self.top_countries_ = countries.value_counts().head(self.top_n).index.tolist()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        frame = self._to_frame(X).copy()
        countries = frame["country"].fillna(self.other_label).astype(str).str.strip()
        frame["country_grouped"] = countries.where(countries.isin(self.top_countries_), self.other_label)
        return frame

    @staticmethod
    def _to_frame(X: pd.DataFrame) -> pd.DataFrame:
        if isinstance(X, pd.DataFrame):
            return X
        return pd.DataFrame(X)
