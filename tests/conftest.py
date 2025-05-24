import pytest
from datetime import datetime, timedelta, timezone

from app.main import app
from app.schemas.schemas import WeatherResponse, WeatherData


@pytest.fixture
def app_fixture():
    return app


@pytest.fixture
def mock_weather_service():
    class MockWeatherService:
        async def get_weather(self, city: str, ip_address: str):
            now = datetime.now(timezone.utc)
            return WeatherResponse(
                city=city,
                latitude=55.75,
                longitude=37.62,
                timezone="Europe/Moscow",
                hourly=[
                    WeatherData(
                        time=now + timedelta(hours=1),
                        temperature=25.0,
                        weather="Солнечно"
                    ),
                    WeatherData(
                        time=now + timedelta(hours=2),
                        temperature=22.0,
                        weather="Облачно"
                    )
                ]
            )
    return MockWeatherService()
