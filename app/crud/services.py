import aiohttp
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from datetime import datetime, timezone

from app.schemas.schemas import WeatherResponse, Failure
from app.config import settings


class WeatherService:
    GEOCODE_URL = settings.GEOCODE_URL
    WEATHER_API_URL = settings.WEATHER_API_URL
    WEATHER_MAP = {
        0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность",
        3: "Пасмурно", 45: "Туман", 48: "Отложение изморози",
        51: "Лёгкая морось", 53: "Умеренная морось", 55: "Плотная морось",
        56: "Лёгкая заморозковая морось", 57: "Плотная заморозковая морось",
        61: "Небольшой дождь", 63: "Умеренный дождь", 65: "Сильный дождь",
        66: "Лёгкий ледяной дождь", 67: "Сильный ледяной дождь",
        71: "Небольшой снег", 73: "Умеренный снег", 75: "Сильный снег",
        77: "Снежные зерна", 80: "Небольшой ливень", 81: "Умеренный ливень",
        82: "Сильный ливень", 85: "Небольшой снегопад", 86: "Сильный снегопад",
        95: "Гроза", 96: "Гроза с небольшим градом", 99: "Гроза с крупным градом",
    }

    async def geocode_city(self, city: str) -> Optional[dict]:
        params = {
            "q": city,
            "format": "json",
            "limit": 1,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.GEOCODE_URL, params=params) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if not data:
                    return None
                return data[0]

    async def get_weather(self, city: str, ip_address: str) -> WeatherResponse | Failure:
        geocode = await self.geocode_city(city)
        if not geocode:
            return Failure(detail=f"Город '{city}' не найден")

        latitude = float(geocode["lat"])
        longitude = float(geocode["lon"])
        display_name = geocode.get("display_name", city)

        url = (
            f"{self.WEATHER_API_URL}"
            f"?latitude={latitude}&longitude={longitude}"
            f"&hourly=temperature_2m,weathercode&timezone=auto"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return Failure(detail=f"Ошибка при получении погоды: {resp.status}")
                data = await resp.json()

                hourly_data = []
                times = data["hourly"]["time"]
                temps = data["hourly"]["temperature_2m"]
                codes = data["hourly"].get("weathercode", [None] * len(times))

                for t, temp, code in zip(times, temps, codes):
                    dt = datetime.fromisoformat(t)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    desc = self.WEATHER_MAP.get(code, "—")
                    hourly_data.append({"time": dt, "temperature": temp, "weather": desc})
                print(WeatherResponse(
                    city=display_name,
                    latitude=latitude,
                    longitude=longitude,
                    timezone=data.get("timezone", "auto"),
                    hourly=hourly_data,
                ))

                return WeatherResponse(
                    city=display_name,
                    latitude=latitude,
                    longitude=longitude,
                    timezone=data.get("timezone", "auto"),
                    hourly=hourly_data,
                )

