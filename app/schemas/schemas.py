from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CityRequest(BaseModel):
    city: str = Field(..., description="Название города для прогноза погоды")


class WeatherData(BaseModel):
    time: datetime
    temperature: float = Field(..., description="Температура (°C)")
    # weathercode: int = Field(None, description="Погодные условия")
    weather: str = Field(None, description="Погодные условия")


class ReturnWeatherData(BaseModel):
    time: datetime
    temperature: float = Field(..., description="Температура (°C)")
    weather: str = Field(None, description="Погодные условия")


class WeatherResponse(BaseModel):
    city: str
    latitude: float
    longitude: float
    timezone: str
    hourly: List[WeatherData]


class Failure(BaseModel):
    detail: str


class CitySearchCount(BaseModel):
    city: str
    count: int
