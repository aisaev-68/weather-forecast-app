from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from fastapi import HTTPException, Depends

from datetime import datetime, timezone
from app.schemas.schemas import CitySearchCount
from app.models.database import get_db

from app.models.models import SearchHistory


class HistorySearchService:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_search_counts(self, ip_address: str) -> List[CitySearchCount]:
        stmt = (
            select(
                SearchHistory.city.label("city"),
                func.sum(SearchHistory.count).label("count")
            )
            .where(SearchHistory.ip_address == ip_address)
            .group_by(SearchHistory.city)
        )
        result = await self.session.execute(stmt)
        rows = result.mappings().all()

        return [CitySearchCount(city=row["city"], count=row["count"]) for row in rows]

    async def insert_search_history(self, data: List[dict]) -> None:
        """
        Сохраняет историю поиска городов с учётом IP пользователя.
        data — список словарей с ключами: city, requested_at (optional), ip_address (optional)
        """
        try:
            async with self.session.begin():
                for entry in data:
                    city = entry['city']
                    ip = entry.get('ip_address')

                    # Поиск существующей записи по городу и IP
                    stmt = select(SearchHistory).where(
                        (SearchHistory.city == city) &
                        (SearchHistory.ip_address == ip)
                    )
                    result = await self.session.execute(stmt)
                    record = result.scalars().first()

                    if record:
                        # Обновляем время запроса и увеличиваем счётчик
                        record.requested_at = datetime.now(timezone.utc)
                        record.count = (record.count or 0) + 1
                    else:
                        # Создаём новую запись с count = 1
                        new_record = SearchHistory(
                            city=city,
                            ip_address=ip,
                            requested_at=entry.get('requested_at', datetime.now(timezone.utc)),
                            count=1
                        )
                        self.session.add(new_record)

            # Коммит автоматически в `async with self.session.begin()`
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=f"DB error: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=f"Unexpected error: {str(e)}")