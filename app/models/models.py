from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP

from app.models.database import Base


class SearchHistory(Base):
    """
    Модель истории запросов погоды.

    Атрибуты:
        id (int): ID записи.
        city (str): Название города.
        requested_at (datetime): Время запроса.
        ip_address (str): IP адрес пользователя (если нужно).
        count (int): Количество запросов по этому городу.
    """
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    requested_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    count: Mapped[int] = mapped_column(Integer, default=1)  # Добавили поле count

    def __repr__(self) -> str:
        return f"<SearchHistory city={self.city} requested_at={self.requested_at} count={self.count}>"

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "city": self.city,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "ip_address": self.ip_address,
            "count": self.count,
        }
