import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse

import sumstats.api_v1.routers.routes as routes_v1
import sumstats.api_v2.routers.eqtl as routes_v2
from sumstats.api_v3.routes import datasets, search, studies
from sumstats.config import (
    API_BASE,
    API_DESCRIPTION,
    APP_VERSION,
    TAGS_METADATA,
)
from sumstats.dependencies.error_classes import APIException

logging.config.fileConfig(
    "sumstats/log_conf.ini", disable_existing_loggers=False
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="eQTL Catalogue Summary Statistics API Documentation",
    openapi_tags=TAGS_METADATA,
    description=API_DESCRIPTION,
    docs_url=f"{API_BASE}/docs",
    redoc_url=None,
    openapi_url=f"{API_BASE}/openapi.json",
    version=APP_VERSION,
)


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )


@app.exception_handler(APIException)
async def handle_custom_api_exception(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )


# configure CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# v1 API (default)
app.include_router(
    routes_v1.router,
    prefix=API_BASE,
    include_in_schema=False,
    default_response_class=ORJSONResponse,
)

app.include_router(
    routes_v1.router,
    prefix=f"{API_BASE}/v1",
    default_response_class=ORJSONResponse,
    deprecated=True,
    tags=["eQTL API v1"],
)
# v2 API
app.include_router(
    routes_v2.router,
    prefix=f"{API_BASE}/v2",
    default_response_class=ORJSONResponse,
    tags=["eQTL API v2"],
)

# v3 API
app.include_router(studies.router)
app.include_router(datasets.router)
app.include_router(search.router)
