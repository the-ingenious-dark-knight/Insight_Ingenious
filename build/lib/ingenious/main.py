import secrets
import sys
import os
import logging
from typing import Annotated
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from ingenious.api.routes import chat, message_feedback, conversation, search
from ingenious.core.logging import setup_logging
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
# from pyautogen.extensions.ingenious import my_extension


# print(my_extension.my_function())

# Load .env file
if os.environ["LOADENV"] == "True":
    load_dotenv(dotenv_path='./config.env')
    # Set up logging
    setup_logging(__package__)

    logger = logging.getLogger(__name__)
else:
    print("Skipping load of environment file")

app = FastAPI(title="FastAgent API", version="1.0.0")

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(message_feedback.router, prefix="/api/v1", tags=["Message Feedback"])
app.include_router(conversation.router, prefix="/api/v1", tags=["Conversation"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])

# Instrument HTTPX - required for OpenAI SDK
# https://github.com/open-telemetry/opentelemetry-python/issues/3693#issuecomment-2014923261
HTTPXClientInstrumentor().instrument()


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):

    if os.environ["LOADENV"] == "True":
        load_dotenv()

        # Log the exception
        logger.exception(exc)

    return JSONResponse(
        status_code=500,
        content={"detail": f"An error occurred: {str(exc)}"}
    )


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the FastAgent API"}


def get_app():
    return app