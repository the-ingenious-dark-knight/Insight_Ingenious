import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from typing_extensions import Annotated
from ingenious.dependencies import get_chat_service
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError
from ingenious.models.chat import ChatRequest
from ingenious.models.http_error import HTTPError
from ingenious.services.chat_service import ChatService
import ingenious.dependencies as igen_deps
import asyncio
import requests
import json
import ingenious.config.config as ingen_config

import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../..'))
sys.path.append(parent_dir)


config = ingen_config.get_config(os.getenv("INGENIOUS_PROJECT_PATH", ""))
logger = logging.getLogger(__name__)
router = APIRouter()


def send_response(response, thread_id, api_key=None):
    """
    Sends the response to the FastAPI API endpoint with optional API key.

    Parameters:
    - response: An object containing the agent's response details.
    - thread_id: The thread ID associated with the response.
    - api_key: (Optional) API key for authentication.
    """
    api_url = config.receiver_configuration.api_url
    headers = {
        "X-API-Key": config.receiver_configuration.api_key,
        "Content-Type": "application/json",
    }

    try:
        # First try to parse the agent_response as JSON
        try:
            agent_response = json.loads(response.agent_response)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            logger.error(f"Raw response: {response.agent_response}")
            # If parsing fails, wrap it in an error response
            payload = {
                "response_id": thread_id,
                "error_flag": True,
                "error_detail": f"Invalid JSON response: {str(e)}"
            }
            print("======")
            print(json.dumps(payload))
            print("======")
            requests.post(api_url, json=payload, headers=headers)
            return

        # Check if we have an error response
        if isinstance(agent_response, dict) and "error" in agent_response:
            payload = {
                "response_id": thread_id,
                "error_flag": True,
                "error_detail": agent_response.get("error", "Unknown error")
            }
            print("======")
            print(json.dumps(payload))
            print("======")
            requests.post(api_url, json=payload, headers=headers)
            return

        # Build the response payload
        response_data = agent_response.get("response", {})
        metadata = agent_response.get("metadata", {})
        entities = metadata.get("entities", {})

        payload = {
            "response_id": thread_id,
            "error_flag": False,
            "error_detail": '',
            "response": {
                "content": response_data.get("content", ""),
                "feedId": response_data.get("feedId", ""),
                "feedTimestamp": response_data.get("feedTimestamp", ""),
                "overBall": response_data.get("overBall", ""),
            },
            "metadata": {
                "match_id": metadata.get("match_id", ""),
                "entities": {
                    "players": entities.get("players", []),
                    "teams": entities.get("teams", []),
                },
            },
        }

        # Check for empty content
        if not payload["response"]["content"]:
            payload = {
                "response_id": thread_id,
                "error_flag": True,
                "error_detail": "Error when processing request, AI cannot identify event type."
            }

    except Exception as e:
        logger.exception(f"Error while sending response to API: {e}")
        payload = {
            "response_id": thread_id,
            "error_flag": True,
            "error_detail": f"Error while sending response to API: {e}"
        }

    # Send the POST request
    print("======")
    print(json.dumps(payload))
    print("======")
    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        logger.info("Response successfully sent to API.")
    else:
        logger.error(
            f"Failed to send response to API. Status code: {response.status_code}"
        )


@router.post(
    "/chat",
    responses={
        200: {"description": "Request Received"},
        400: {"model": HTTPError, "description": "Bad Request"},
        406: {"model": HTTPError, "description": "Not Acceptable"},
        413: {"model": HTTPError, "description": "Payload Too Large"},
        500: {"model": HTTPError, "description": "Internal Server Error"},
    },
    status_code=200,  # Default response status for acknowledgment
)
async def chat(
    chat_request: ChatRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    credentials: Annotated[HTTPBasicCredentials, Depends(igen_deps.get_security_service)],
):
    """
    Handles chat requests and acknowledges receipt.
    """
    try:
        # Log acknowledgment
        logger.info(f"Request received for conversation_flow: {chat_request.conversation_flow}")

        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        # Perform asynchronous processing
        async def process_chat():
            try:
                response = await chat_service.get_chat_response(chat_request)
                send_response(response, chat_request.thread_id)
            except Exception as e:
                logger.exception(f"Error processing chat: {e}")

        # Schedule the processing task
        asyncio.create_task(process_chat())

        # Return acknowledgment immediately
        return {"message": "Request received and processing"}

    except ValueError as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
    except ContentFilterError as cfe:
        logger.exception(cfe)
        raise HTTPException(status_code=406, detail=ContentFilterError.DEFAULT_MESSAGE)
    except TokenLimitExceededError as tle:
        logger.exception(tle)
        raise HTTPException(status_code=413, detail=TokenLimitExceededError.DEFAULT_MESSAGE)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
