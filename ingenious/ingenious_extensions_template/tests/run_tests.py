import json
import datetime
from pathlib import Path
import jsonpickle
import markdown
import os
from jinja2 import Environment, FileSystemLoader
# Ingenious imports
import ingenious.config.config as ingen_config
from ingenious.models.chat import ChatRequest
from ingenious.services.chat_service import ChatService
from ingenious.files.files_repository import FileStorage
import ingenious.dependencies as ingen_deps
from ingenious.utils.stage_executor import ProgressConsoleWrapper
from ingenious.utils.model_utils import Object_To_Yaml
from ingenious.utils.namespace_utils import get_file_from_namespace_with_fallback
# Ingenious Extensions 
import ingenious_extensions.models.ca_raw_fixture_data as gm



class RunBatches:
    def __init__(self, progress: ProgressConsoleWrapper, task_id: str = None):
        self.config = ingen_config.get_config()
        self.fs = FileStorage(config=self.config)
        self.progress = progress
        self.task_id = task_id
        self.directory = "example_payload/raw"

    async def run(self):
        # placeholder for testing process