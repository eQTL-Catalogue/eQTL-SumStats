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
DESCRIPTION = """
<img src='https://raw.githubusercontent.com/eQTL-Catalogue/eQTL-Catalogue-website/gh-pages/static/eQTL_icon.png' alt="eqtl_icon" width="10%">

Welcome to the [eQTL Catalogue](https://www.ebi.ac.uk/eqtl) RESTful API.

This API is for facilitating  a filtered request of 
eQTL association data.

## API v2

Each study in the catalogue is split by QTL context and these splits are
assigned their own dataset IDs (QTD#). Datasets can be browsed at the `/datasets` 
endpoint. 

To retrieve the summary statistics for a dataset, use the 
`/datasets/<DATASETID>/associations` endpoint and apply 
any required filters. 

## API v1

This will be deprecated and is maintained only for existing integrations. 

## All associations
If you are interested in downloading 
_all_ the association data for a dataset, the recommended 
method would be via the FTP.

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
              description=DESCRIPTION,
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
