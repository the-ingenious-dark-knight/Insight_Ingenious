from abc import ABC, abstractmethod
import logging
from fastapi import APIRouter, FastAPI
from ingenious.models.config import Config
from ingenious.dependencies import get_security_service, get_chat_history_repository
from fastapi.security import HTTPBasicCredentials


class IApiRoutes(ABC):
    def __init__(self, config: Config, app: FastAPI):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.app = app
        self.security_service = get_security_service(HTTPBasicCredentials)
        self.chat_history_repository = get_chat_history_repository()

    @abstractmethod
    def add_custom_routes(self) -> APIRouter:
        """
        Adds custom routes to the FastAPI app instance. Always returns the router instance.
        """
        pass
