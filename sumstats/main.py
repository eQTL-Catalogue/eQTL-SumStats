from fastapi import FastAPI
import sumstats.api_v1.routers.routes as routes_v1

API_BASE = "/eqtl/api"

def create_app():
    app = FastAPI(title="EQTL summary statistics API")
    # v1 API (default)
    app.include_router(routes_v1.router, prefix=API_BASE, include_in_schema=False)
    app.include_router(routes_v1.router, prefix=f"{API_BASE}/v1")
    # v2 API
    return app


app = create_app()