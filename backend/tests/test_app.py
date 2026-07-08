from fastapi.testclient import TestClient

from invictus_os.api.app import create_app
from invictus_os.config.settings import get_settings


def test_app_allows_vercel_frontend_origins() -> None:
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.options(
        "/health",
        headers={
            "Origin": "https://invictus-os-frontend.vercel.app",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "https://invictus-os-frontend.vercel.app"
    )


def test_app_allows_local_frontend_origin() -> None:
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
