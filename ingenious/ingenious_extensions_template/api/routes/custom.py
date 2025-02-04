from fastapi import FastAPI, APIRouter
from ingenious.models.api_routes import IApiRoutes
router = APIRouter()


class Api_Routes(IApiRoutes):
    def add_custom_routes(self) -> FastAPI:
        @router.post(
            "/chat_custom_sample"
        )
        def chat_custom_sample():
            # return success
            return "OK"

        self.app.include_router(
            router, prefix="/api/v1", tags=["chat_custom_sample"]
        )
        return self.app.router

