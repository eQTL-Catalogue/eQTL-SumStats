from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from sumstats.dependencies.error_classes import APIException
import sumstats.api_v1.routers.routes as routes_v1


API_BASE = "/eqtl/api"


def create_app():
    app = FastAPI(title="EQTL summary statistics API")
    
    @app.exception_handler(APIException)
    async def handle_custom_api_exception(request: Request, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message},
        )
    
    # configure CORS
    app.add_middleware(CORSMiddleware, 
                       allow_origins=['*'])
    # v1 API (default)
    app.include_router(routes_v1.router, prefix=API_BASE,
                       include_in_schema=False)
    app.include_router(routes_v1.router, prefix=f"{API_BASE}/v1")
    # v2 API
    return app


app = create_app()