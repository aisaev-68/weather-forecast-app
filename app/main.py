from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from starlette.templating import _TemplateResponse as TemplateResponse

from app.api.api import api_router as api_router_v1
from app.schemas.schemas import Failure
from app.models.database import engine, Base
from app.utils.logger import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Инициализация БД при старте"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ База данных создана")

    yield

    await engine.dispose()
    logger.info("🔒 Соединение с базой данных закрыто")


app = FastAPI(
    title="Weather app",
    description="Тестовое задание.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url='/api/redoc',
    responses={
        422: {
            "description": "Ошибка проверки",
            "model": Failure,
        },
    },
    lifespan=lifespan,
)

templates = Jinja2Templates(directory="www/data/templates")

origins = [
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router_v1)


@app.get("/", include_in_schema=False)
async def index(request: Request) -> TemplateResponse:
    """Переход на главную страницу"""

    logger.info("Переход на главную страницу")
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)