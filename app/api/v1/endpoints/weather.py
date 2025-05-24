from datetime import datetime, timezone
from fastapi import Request, APIRouter, Depends, Body, HTTPException, status
from typing import Annotated, Union, List

from app.schemas.schemas import CityRequest, WeatherResponse, Failure, CitySearchCount
from app.crud.services import WeatherService
from app.crud.search_history_service import HistorySearchService
from app.utils.logger import get_logger

logger = get_logger("api.weather")
router = APIRouter()


@router.post(
    "/weather",
    response_model=Union[WeatherResponse, Failure],
    summary="Получить прогноз погоды по названию города",
    description="Принимает название города и возвращает прогноз погоды на ближайшее время.",
    status_code=status.HTTP_200_OK,
)
async def get_weather(
        request: Request,
        service: Annotated[WeatherService, Depends()],
        search_history_service: Annotated[HistorySearchService, Depends()],
        params: CityRequest = Body(...),
) -> Union[WeatherResponse, Failure]:
    """
    Эндпоинт для получения прогноза погоды по названию города.

    ### params:
    - **request**: Request — Объект запроса FastAPI. Используется для получения IP-адреса клиента.
    - **service**: WeatherService — Сервис для работы с погодным API и сохранения истории запросов.
    - **params**: CityRequest — Тело запроса, содержащее название города (параметр `city`).

    ### return:
    - `WeatherResponse` — Объект с информацией о погоде, если город найден.
    - `Failure` — Объект с описанием ошибки, если город не найден или произошла ошибка API.
    """
    ip_address = request.client.host
    result = await service.get_weather(params.city, ip_address)
    print(result)

    if isinstance(result, Failure):
        raise HTTPException(status_code=400, detail=result.detail)

    await search_history_service.insert_search_history([
        {
            "city": params.city,
            "ip_address": ip_address,
            "requested_at": datetime.now(timezone.utc)
        }
    ])

    now_utc = datetime.now(timezone.utc)

    filtered = []
    for entry in result.hourly:
        dt = entry.time
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        if dt >= now_utc:
            filtered.append(entry)

    result.hourly = filtered[:6]

    logger.info(f"Прогноз погоды для города: {params.city}")

    return result

@router.get(
    "/search-history",
    response_model=List[CitySearchCount],
    summary="Получить статистику запросов по городам",
    description="Возвращает список городов с количеством раз, сколько их искали пользователи.",
    status_code=status.HTTP_200_OK,
)
async def get_search_history(
        request: Request,
        service: Annotated[HistorySearchService, Depends()],
) -> List[CitySearchCount]:
    """
    Эндпоинт для получения статистики по истории поисков городов.

    ### Возвращает:
    - Список объектов `CitySearchCount`, где каждый объект содержит:
      - `city` (str): Название города.
      - `count` (int): Количество раз, сколько этот город запрашивали.
    """
    ip_address = request.client.host
    history = await service.get_search_counts(ip_address)
    return history
