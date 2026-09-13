from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ItemFeatures(Base):
    __tablename__ = "item_features"

    item_id: Mapped[str] = mapped_column(primary_key=True)
    historical_return_rate: Mapped[float]
    avg_item_losses_30d: Mapped[float]
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"ItemFeatures(item_id={self.item_id!r}, updated_at={self.updated_at!r})"


class Prediction(Base):
    __tablename__ = "predictions"

    request_id: Mapped[str] = mapped_column(primary_key=True)
    prediction: Mapped[float]
    model_version: Mapped[str]
    item_id: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"Prediction(request_id={self.request_id!r}, prediction={self.prediction!r})"
