import json
from pathlib import Path

import joblib
import pandas as pd

from app.config import settings


class Predictor:
    def __init__(self, model, feature_order: list[str], model_version: str) -> None:
        self._model = model
        self._feature_order = feature_order
        self.model_version = model_version

    def predict(self, features: dict) -> float:
        df = pd.DataFrame([features])[self._feature_order]
        result = self._model.predict(df)
        return float(result[0])

    def __repr__(self) -> str:
        return f"Predictor(model_version={self.model_version!r})"

def load_predictor() -> Predictor:
    metadata = json.loads(
        Path(settings.model_metadata_path).read_text(encoding="utf-8")
    )
    model = joblib.load(settings.model_path)
    return Predictor(
        model=model,
        feature_order=metadata["features"],
        model_version=metadata["model_version"],
    )
