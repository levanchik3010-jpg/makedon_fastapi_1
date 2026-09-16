import logging
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.category import router as category_router
from app.api.routers.task import router as task_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     Base.metadata.create_all(bind=engine)
#     yield

app = FastAPI()

request_counter = 0

logger = logging.getLogger("app.middleware")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    global request_counter
    request_counter += 1
    current_request_num = request_counter
    started_at = perf_counter()
    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "Request failed: %s %s completed_in=%.2fms",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    response.headers["X-Request-Number"] = str(current_request_num)
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    return response


app.include_router(task_router)
app.include_router(category_router)
