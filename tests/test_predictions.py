from datetime import datetime, timezone

from app.db_models import ItemFeatures, Prediction


def _add_item(
    db_session,
    item_id="ITEM-001",
    historical_return_rate=0.5,
    avg_item_losses_30d=100.0,
):
    db_session.add(
        ItemFeatures(
            item_id=item_id,
            historical_return_rate=historical_return_rate,
            avg_item_losses_30d=avg_item_losses_30d,
            updated_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()


def test_successful_prediction(client, db_session):
    _add_item(db_session)

    response = client.post(
        "/predictions",
        json={
            "request_id": "req-1",
            "item_id": "ITEM-001",
            "item_price": 2500.0,
            "delivery_days": 4,
            "client_is_app": True,
            "type_prepayment": "card",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "req-1"
    assert isinstance(body["prediction"], float)
    assert body["model_version"] == "1.0.0"


def test_validation_error(client):
    response = client.post(
        "/predictions",
        json={
            "request_id": "req-2",
            "item_id": "ITEM-001",
            "item_price": 2500.0,
            "delivery_days": 4,
            "client_is_app": True,
            "type_prepayment": "qiwi",
        },
    )

    assert response.status_code == 422


def test_item_not_found(client):
    response = client.post(
        "/predictions",
        json={
            "request_id": "req-3",
            "item_id": "ITEM-NOPE",
            "item_price": 2500.0,
            "delivery_days": 4,
            "client_is_app": True,
            "type_prepayment": "card",
        },
    )

    assert response.status_code == 404


def test_repeated_request_id_returns_first_result(client, db_session):
    _add_item(db_session)
    payload = {
        "request_id": "req-4",
        "item_id": "ITEM-001",
        "item_price": 2500.0,
        "delivery_days": 4,
        "client_is_app": True,
        "type_prepayment": "card",
    }

    first = client.post("/predictions", json=payload)
    assert first.status_code == 200

    different_payload = {**payload, "item_price": 999.0}
    second = client.post("/predictions", json=different_payload)

    assert second.status_code == 200
    assert second.json() == first.json()

    count = db_session.query(Prediction).filter_by(request_id="req-4").count()
    assert count == 1


def test_get_stored_prediction(client, db_session):
    _add_item(db_session)
    payload = {
        "request_id": "req-5",
        "item_id": "ITEM-001",
        "item_price": 2500.0,
        "delivery_days": 4,
        "client_is_app": True,
        "type_prepayment": "card",
    }
    post_response = client.post("/predictions", json=payload)

    get_response = client.get("/predictions/req-5")

    assert get_response.status_code == 200
    assert get_response.json() == post_response.json()


def test_get_unknown_prediction_returns_404(client):
    response = client.get("/predictions/unknown-id")
    assert response.status_code == 404
