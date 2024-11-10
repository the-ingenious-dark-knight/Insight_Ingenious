import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from chainlit.utils import mount_chainlit
from dotenv import load_dotenv
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
import logging
import ingenious.config.config as ingen_config

# Import your routers
import ingenious.api.routes.chat as chat
import ingenious.api.routes.message_feedback as message_feedback
# import conversation
# import search
import importlib.resources as pkg_resources

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class FastAgentAPI:
    def __init__(self, config: ingen_config.Config):
        # Set the working directory
        os.chdir(os.environ["INGENIOUS_WORKING_DIR"])

        # Initialize FastAPI app
        self.app = FastAPI(title="FastAgent API", version="1.0.0")

        # Include routers
        self.app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
        self.app.include_router(message_feedback.router, prefix="/api/v1", tags=["Message Feedback"])
        # self.app.include_router(conversation.router, prefix="/api/v1", tags=["Conversation"])
        # self.app.include_router(search.router, prefix="/api/v1", tags=["Search"])

        # Instrument HTTPX - required for OpenAI SDK
        # https://github.com/open-telemetry/opentelemetry-python/issues/3693#issuecomment-2014923261
        HTTPXClientInstrumentor().instrument()

        # Add exception handler
        self.app.add_exception_handler(Exception, self.generic_exception_handler)

        # Add root endpoint
        self.app.get("/", tags=["Root"])(self.root)

        #Mount ChainLit
        if config.chainlit_configuration.enable:
            chainlit_path = pkg_resources.files("ingenious.chainlit") / "app.py"
            mount_chainlit(app=self.app, target=str(chainlit_path), path="/chainlit")

            # chainlit_path_2 = pkg_resources.files("ingenious.chainlit") / "app_classification.py"
            # mount_chainlit(app=self.app, target=str(chainlit_path_2), path="/chainlit_classification")


    async def generic_exception_handler(self, request: Request, exc: Exception):
        if os.environ.get("LOADENV") == "True":
            load_dotenv()

        # Log the exception
        logger.exception(exc)

        return JSONResponse(
            status_code=500,
            content={"detail": f"An error occurred: {str(exc)}"}
        )

    async def root(self):
        # Locate the HTML file in ingenious.api
        html_path = pkg_resources.files("ingenious.chainlit") / "index.html"
        with html_path.open("r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
