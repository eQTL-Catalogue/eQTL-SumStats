from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from sumstats.dependencies.error_classes import APIException
import sumstats.api_v1.routers.routes as routes_v1
import sumstats.api_v2.routers.eqtl as routes_v2


logging.config.fileConfig("sumstats/log_conf.ini",
                          disable_existing_loggers=False)
logger = logging.getLogger(__name__)

API_BASE = "/eqtl/api"

description = """
Placeholder
"""

tags_metadata = [
    {
        "name": "eQTL API v2",
        "description": "REST API for accessing eQTL summary statistics data",
    },
    {
        "name": "eQTL API v1",
        "description": "**Deprecated** REST API for accessing eQTL summary statistics data",
    }
]


app = FastAPI(title="eQTL Catalogue Summary Statistics API Documentation",
              openapi_tags=tags_metadata,
              description=description,
              docs_url=f"{API_BASE}/docs",
              redoc_url=None,
              openapi_url=f"{API_BASE}/openapi.json")


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )


@app.exception_handler(APIException)
async def handle_custom_api_exception(request: Request,
                                      exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )

# configure CORS
app.add_middleware(CORSMiddleware, 
                   allow_origins=['*'])

# v1 API (default)
app.include_router(routes_v1.router,
                   prefix=API_BASE,
                   include_in_schema=False,
                   default_response_class=ORJSONResponse)

app.include_router(routes_v1.router,
                   prefix=f"{API_BASE}/v1",
                   default_response_class=ORJSONResponse,
                   deprecated=True,
                   tags=["eQTL API v1"])
# v2 API
app.include_router(routes_v2.router,
                   prefix=f"{API_BASE}/v2",
                   tags=["eQTL API v2"])
