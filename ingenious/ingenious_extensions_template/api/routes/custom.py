

from urllib.error import HTTPError
from fastapi import FastAPI

from ingenious.models.api_routes import IApiRoutes


class Api_Routes(IApiRoutes):
    def add_custom_routes(self) -> FastAPI:
        @self.router.post(
            "/chat2"
        )
        def chat2():
            # return success
            return "OK"

        return self.router
 
