from fastapi import FastAPI
import sumstats.api_v1.routers.routes as routes_v1



def create_app():
    app = FastAPI(title="EQTL summary statistics API")
    # v1 API (default)
    app.include_router(routes_v1.router, prefix="", include_in_schema=False)
    app.include_router(routes_v1.router, prefix="/v1")
    # v2 API
    return app


app = create_app()