from datetime import datetime, timezone

from app.db_models import ItemFeatures
from app.features_loader import load_item_features


def test_load_item_features_upserts_and_skips_bad_rows(db_session, tmp_path):
    csv_content = (
        "item_id,historical_return_rate,avg_item_losses_30d,updated_at\n"
        "ITEM-001,0.5,100.0,2026-01-01T00:00:00Z\n"
        "ITEM-002,1.5,50.0,2026-01-01T00:00:00Z\n"  # вне диапазона
        "ITEM-003,0.3,-10.0,2026-01-01T00:00:00Z\n"  # отрицательное
        "ITEM-004,not_a_number,10.0,2026-01-01T00:00:00Z\n"  # не число
    )
    csv_path = tmp_path / "item_features.csv"
    csv_path.write_text(csv_content, encoding="utf-8")

    load_item_features(str(csv_path), db_session)

    rows = db_session.query(ItemFeatures).all()
    assert [row.item_id for row in rows] == ["ITEM-001"]


def test_load_item_features_last_valid_row_wins(db_session, tmp_path):
    csv_content = (
        "item_id,historical_return_rate,avg_item_losses_30d,updated_at\n"
        "ITEM-001,0.1,10.0,2026-01-01T00:00:00Z\n"
        "ITEM-001,0.9,900.0,2026-02-01T00:00:00Z\n"
    )
    csv_path = tmp_path / "item_features.csv"
    csv_path.write_text(csv_content, encoding="utf-8")

    load_item_features(str(csv_path), db_session)

    row = db_session.get(ItemFeatures, "ITEM-001")
    assert row.historical_return_rate == 0.9
    assert row.avg_item_losses_30d == 900.0


def test_load_item_features_updates_existing_row(db_session):
    db_session.add(
        ItemFeatures(
            item_id="ITEM-001",
            historical_return_rate=0.1,
            avg_item_losses_30d=10.0,
            updated_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()

    csv_content = (
        "item_id,historical_return_rate,avg_item_losses_30d,updated_at\n"
        "ITEM-001,0.7,500.0,2026-03-01T00:00:00Z\n"
    )

    import os
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(csv_content)

    load_item_features(path, db_session)
    os.remove(path)

    row = db_session.get(ItemFeatures, "ITEM-001")
    assert row.historical_return_rate == 0.7
    assert db_session.query(ItemFeatures).count() == 1
