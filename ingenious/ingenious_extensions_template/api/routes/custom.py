

from urllib.error import HTTPError
from fastapi import APIRouter, FastAPI

from ingenious.models.api_routes import IApiRoutes


class Api_Routes(IApiRoutes):
    def add_custom_routes(self) -> FastAPI:
        router: APIRouter = APIRouter()

        @router.post(
            "/chat2"
        )
        def chat2():
            # return success
            return "OK"
        
        self.app.include_router(
            router, prefix="/api/v1", tags=["chat2"]
        )
        return self.app.router

