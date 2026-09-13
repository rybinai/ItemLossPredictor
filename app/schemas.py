from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    item_id: str
    item_price: float = Field(gt=0)
    delivery_days: int = Field(ge=0)
    client_is_app: bool
    type_prepayment: Literal["card", "cash", "sbp"]


class PredictionResponse(BaseModel):
    request_id: str
    prediction: float
    model_version: str

    @field_serializer("prediction")
    def _round_prediction(self, value: float) -> float:
        return round(value, 2)
