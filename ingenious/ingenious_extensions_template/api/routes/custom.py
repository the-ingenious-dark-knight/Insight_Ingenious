import asyncio
import logging
from fastapi.security import HTTPBasicCredentials
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, FastAPI
from ingenious.config import config
from ingenious.dependencies import get_chat_service
from ingenious.files import files_repository
from ingenious.models.api_routes import IApiRoutes
from ingenious.models.chat import ChatRequest, ChatResponse
import ingenious.dependencies as igen_deps
from ingenious.services.chat_service import ChatService


class Api_Routes(IApiRoutes):
    def add_custom_routes(self) -> FastAPI:
        
        router = APIRouter()

        @router.post(
            "/chat_custom_sample"
        )
        async def chat_custom_sample(
            chat_request: ChatRequest,
            chat_service: Annotated[ChatService, Depends(get_chat_service)],
            credentials: Annotated[
                HTTPBasicCredentials, Depends(igen_deps.get_security_service)
                ]
        ) -> ChatResponse:
            pass
        
        self.app.include_router(
            router, prefix="/api/v1", tags=["chat_custom_sample"]
        )
        return self.app.router

