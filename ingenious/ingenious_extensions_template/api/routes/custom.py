#
#
# from urllib.error import HTTPError
# from fastapi import FastAPI, APIRouter
# from ingenious.models.api_routes import IApiRoutes
# router = APIRouter()
#
#
# class Api_Routes(IApiRoutes):
#     def add_custom_routes(self) -> FastAPI:
#         @router.post(
#             "/chat2"
#         )
#         def chat2():
#             # return success
#             return "OK"
#
#         self.app.include_router(
#             router, prefix="/api/v1", tags=["chat_async"]
#         )
#         return self.app.router
#
