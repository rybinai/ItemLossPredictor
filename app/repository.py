from sqlalchemy.orm import Session

from app.db_models import ItemFeatures, Prediction


def get_item_features(session: Session, item_id: str) -> ItemFeatures | None:
    return session.get(ItemFeatures, item_id)


def get_request_prediction(session: Session, request_id: str) -> Prediction | None:
    return session.get(Prediction, request_id)


def save_prediction(
    session: Session,
    request_id: str,
    prediction: float,
    model_version: str,
    item_id: str,
) -> Prediction:
    row = Prediction(
        request_id=request_id,
        item_id=item_id,
        prediction=prediction,
        model_version=model_version,
    )
    session.add(row)
    session.commit()
    return row
