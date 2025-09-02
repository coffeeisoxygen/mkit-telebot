# ruff : noqa

from pathlib import Path
import uvicorn
from fastapi import FastAPI

# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.config import get_settings
from app.custom import LoggingMiddleware, setup_logging
from app.custom.exception import register_exception_handlers
from app.api import setup_router

from contextlib import asynccontextmanager
from app.database import DatabaseSessionManager
from app.services.users import seed_default_admin
from app.repositories.repo_user import UserRepository
from app.services.hasher.argonhasher import Argon2Hasher


# 1. Setup settings and logging
settings = get_settings()
logconfigpath = Path(__file__).parent.parent / "config_log.yaml"
setup_logging(config_path=logconfigpath, env=settings.ENV.environment.value)


# Setup DatabaseSessionManager for lifespan
sessionmanager = DatabaseSessionManager(settings.DB.url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log = logger.bind(context="lifespan")
    log.info("Application starting up.")
    log.info(f"ADM config: {settings.ADM.model_dump()}")
    async with sessionmanager.session() as db_session:
        repo = UserRepository(db_session)
        hasher = Argon2Hasher()
        admin_config = settings.ADM
        await seed_default_admin(repo, hasher, admin_config)

    yield

    log.info("Application shutting down.")
    await sessionmanager.close()


# 2. Inisialisasi FastAPI app
app = FastAPI(
    title=settings.ENV.name,
    version=settings.ENV.version,
    debug=settings.ENV.debug,
    description="Aplikasi Telegram BOT untuk Kirim pesan ke channel otomatis",
    lifespan=lifespan,
)

# 3. Registrasi exception handler
register_exception_handlers(app)

# 4. Mount static files dan templates
# app.mount("/static", StaticFiles(directory="app/views/static"), name="static")
# templates = Jinja2Templates(directory="app/views/templates")

# 5. Tambahkan middlewares
origins = ["*"]

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(middleware_class=LoggingMiddleware)

# 6. Setup router
setup_router(app)


# # 7. Endpoint render index.html (UI)
# @app.get("/ui")
# async def ui_index(request: Request):
#     """Render UI index page."""
#     return templates.TemplateResponse("index.html", {"request": request})


# 8. Default root endpoint
@app.get("/")
async def root():  # noqa: D103
    return {"message": "Hello World"}


# 9. Main guard
if __name__ == "__main__":
    logger.info("Running application with Uvicorn...")
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,
        log_level=None,
    )
