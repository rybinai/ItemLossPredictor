import csv
from datetime import datetime

from sqlalchemy.orm import Session

from app.db_models import ItemFeatures


def _parse_row(row: dict[str, str]) -> dict | None:
    item_id = row.get("item_id", "").strip()
    if not item_id:
        return None

    try:
        historical_return_rate = float(row["historical_return_rate"])
        avg_item_losses_30d = float(row["avg_item_losses_30d"])
    except (KeyError, ValueError):
        return None

    if not (0 <= historical_return_rate <= 1):
        return None
    if avg_item_losses_30d < 0:
        return None

    try:
        updated_at = datetime.fromisoformat(row["updated_at"])
    except (KeyError, ValueError):
        return None

    return {
        "item_id": item_id,
        "historical_return_rate": historical_return_rate,
        "avg_item_losses_30d": avg_item_losses_30d,
        "updated_at": updated_at,
    }


def load_item_features(csv_path: str, session: Session) -> None:
    valid_rows: dict[str, dict] = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            parsed = _parse_row(raw_row)
            if parsed is None:
                continue
            valid_rows[parsed["item_id"]] = parsed

    for item_id, data in valid_rows.items():
        existing = session.get(ItemFeatures, item_id)
        if existing is not None:
            existing.historical_return_rate = data["historical_return_rate"]
            existing.avg_item_losses_30d = data["avg_item_losses_30d"]
            existing.updated_at = data["updated_at"]
        else:
            session.add(ItemFeatures(**data))
    session.commit()


if __name__ == "__main__":
    import sys

    from app.db import SessionLocal

    csv_path = sys.argv[1]
    with SessionLocal() as session:
        load_item_features(csv_path, session)
