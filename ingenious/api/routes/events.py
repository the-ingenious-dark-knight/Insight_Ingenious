
import asyncio
import logging
from pathlib import Path
from fastapi.security import HTTPBasicCredentials
import jsonpickle
from pydantic import BaseModel
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import ingenious.dependencies as igen_deps
from ingenious.files.files_repository import FileStorage

logger = logging.getLogger(__name__)
router = APIRouter()

