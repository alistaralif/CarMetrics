import time
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from contextlib import asynccontextmanager
from app.api.router import api_router
from app.api.routes.admin import router as admin_router
from app.db.cache import init_cache_db
from app.db.logging import init_logging_db, log_api_call
from app.db.log_retention import archive_completed_months
from http import HTTPStatus
from fastapi.middleware.cors import CORSMiddleware
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    init_cache_db()
    init_logging_db()
    archive_completed_months()
    yield
    # ---- shutdown ----
    # (nothing needed yet)

app = FastAPI(
    title="CarMetrics API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "https://carmetrics.fly.dev",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],        # allows OPTIONS, POST, etc
    allow_headers=["*"],        # allows Content-Type, X-Request-ID, etc
)


@app.middleware("http")
async def timing_and_logging(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start = time.perf_counter()
    response = await call_next(request)
    duration = round(time.perf_counter() - start, 4)

    # Expose to client
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.4f}s"

    ip_address = (
        request.headers.get("fly-client-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else None)
    )

    if request.url.path.startswith("/api"):
        log_api_call(
            endpoint=request.url.path,
            userrole=getattr(request.state, "userrole", None),
            url_count=getattr(request.state, "url_count", None),
            process_time=duration,
            status_code=response.status_code,
            status_text=HTTPStatus(response.status_code).phrase,
            ip_address=ip_address,
            request_id=request_id,
        )

    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """ Handles HTTP exceptions raised in endpoints. """
    request_id = getattr(request.state, "request_id", None)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HttpError",
            "message": exc.detail,
            "request_id": request_id,
        },
    )
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """ Handles request payload validation errors (422). """
    request_id = getattr(request.state, "request_id", None)

    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Invalid request payload",
            "details": exc.errors(),
            "request_id": request_id,
        },
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """ Handles all uncaught exceptions (500). """
    request_id = getattr(request.state, "request_id", None)

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "request_id": request_id,
        },
    )


app.include_router(api_router, prefix="/api")
app.include_router(admin_router)