from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import repository
from app.db import get_session
from app.ml import Predictor
from app.schemas import PredictionRequest, PredictionResponse

router = APIRouter()


def get_predictor(request: Request) -> Predictor:
    return request.app.state.predictor


@router.post("/predictions", response_model=PredictionResponse)
def create_prediction(
    req: PredictionRequest,
    session: Session = Depends(get_session),
    predictor: Predictor = Depends(get_predictor),
) -> PredictionResponse:
    existing = repository.get_request_prediction(session, req.request_id)
    if existing is not None:
        return PredictionResponse(
            request_id=existing.request_id,
            prediction=existing.prediction,
            model_version=existing.model_version,
        )

    item = repository.get_item_features(session, req.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")

    features = {
        "item_price": req.item_price,
        "delivery_days": req.delivery_days,
        "client_is_app": req.client_is_app,
        "type_prepayment": req.type_prepayment,
        "historical_return_rate": item.historical_return_rate,
        "avg_item_losses_30d": item.avg_item_losses_30d,
    }
    value = predictor.predict(features)

    row = repository.save_prediction(
        session,
        request_id=req.request_id,
        item_id=req.item_id,
        prediction=value,
        model_version=predictor.model_version,
    )

    return PredictionResponse(
        request_id=row.request_id,
        prediction=row.prediction,
        model_version=row.model_version,
    )


@router.get("/predictions/{request_id}", response_model=PredictionResponse)
def get_prediction(
    request_id: str, session: Session = Depends(get_session)
) -> PredictionResponse:
    row = repository.get_request_prediction(session, request_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return PredictionResponse(
        request_id=row.request_id,
        prediction=row.prediction,
        model_version=row.model_version,
    )
