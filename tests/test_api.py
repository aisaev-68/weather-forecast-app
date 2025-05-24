from fastapi.testclient import TestClient

from app.crud.services import WeatherService


def test_get_weather_success(app_fixture, mock_weather_service):
    app_fixture.dependency_overrides[WeatherService] = lambda: mock_weather_service

    with TestClient(app_fixture) as client:
        response = client.post("/api/weather", json={"city": "Moscow"})
        assert response.status_code == 200
        data = response.json()

        assert "city" in data
        assert data["city"] == "Moscow"
        assert "hourly" in data
        assert isinstance(data["hourly"], list)
        assert len(data["hourly"]) > 0


def test_get_weather_failure(app_fixture, mock_weather_service):
    app_fixture.dependency_overrides[WeatherService] = lambda: mock_weather_service

    with TestClient(app_fixture) as client:
        response = client.post("/api/weather", json={"city": "UnknownCity"})
        data = response.json()
        assert response.status_code == 200
        assert "UnknownCity" == data['city']


