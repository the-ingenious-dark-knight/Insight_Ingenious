import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated
from ingenious.dependencies import get_chat_service
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.models.http_error import HTTPError
from ingenious.services.chat_service import ChatService
import ingenious.dependencies as igen_deps
import ingenious.utils.namespace_utils as ns_utils

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/diagnostic",
    responses={
        400: {"model": HTTPError, "description": "Bad Request"},
        406: {"model": HTTPError, "description": "Not Acceptable"},
        413: {"model": HTTPError, "description": "Payload Too Large"},
    },
)
async def diagnostic(    
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_security_service)
    ]
):
    try:
        diagnostic = {}
        
        prompt_dir = Path(
                await igen_deps.get_file_storage_revisions().get_base_path()
            ) / Path(
                await igen_deps.get_file_storage_revisions().get_prompt_template_path()
            )
        
        data_dir = Path(
                await igen_deps.get_file_storage_data().get_base_path()
            ) / Path(
                await igen_deps.get_file_storage_data().get_base_path()
            )

        diagnostic["Prompt Directory"] = prompt_dir
        diagnostic["Data Directory"] = data_dir
        
        return diagnostic

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
