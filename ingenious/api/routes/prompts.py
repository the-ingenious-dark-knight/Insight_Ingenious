
import asyncio
import logging
from pathlib import Path
from fastapi.security import HTTPBasicCredentials
import jsonpickle
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
import ingenious.dependencies as igen_deps
from ingenious.files.files_repository import FileStorage

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/prompts/view/{revision_id}/{filename}")
def view(
    revision_id: str,
    filename: str,
    request: Request,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_security_service)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
    
):
    prompt_template_folder = asyncio.run(fs.get_prompt_template_path(revision_id=revision_id))
    content = asyncio.run(fs.read_file(file_name=filename, file_path=prompt_template_folder))
    return content

@router.get("/prompts/list/{revision_id}")
def list(
    revision_id: str,
    request: Request,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_security_service)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
):
    prompt_template_folder = asyncio.run(fs.get_prompt_template_path(revision_id=revision_id))
    
    try:
        files_raw = asyncio.run(fs.list_files(file_path=prompt_template_folder))
        files = sorted([Path(f).name for f in files_raw if f.endswith(('.md', '.jinja'))])
    except FileNotFoundError:
        files = []
    return files
