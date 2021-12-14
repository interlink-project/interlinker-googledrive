from fastapi import APIRouter
from app.old.endpoints import router
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from app.google import service
from app.utils.config import settings

app = FastAPI(
    title="Google Drive API Wrapper", openapi_url=f"{settings.API_V1_STR}/openapi.json", docs_url="/googledrive/docs"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # localhost only
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/googledrive")
def main():
    return RedirectResponse(url="/googledrive/docs")

@app.get("/googledrive/healthcheck")
def healthcheck():
    return True

api_router = APIRouter()
api_router.include_router(router, prefix="/assets", tags=["assets"])


app.include_router(api_router, prefix=settings.API_V1_STR)

###################
# Repeated tasks
###################


sessionmaker = FastAPISessionMaker(settings.SQLALCHEMY_DATABASE_URI)

@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # 1 hour
def repetitive_task() -> None:
    pass
    # clean(db)
