import datetime
import json
from typing import List

import jsonpickle
from ingenious.models.chat import ChatRequest
from ingenious.models.config import Config
from ingenious.files.files_repository import FileStorage
from ingenious.services.chat_service import ChatService
import ingenious.dependencies as ingen_deps
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback
import os
from ingenious.models.agent import Agent


class functional_tests:
    def __init__(self, config: Config):
        self.config = ingen_deps.get_config()
        self.fs = FileStorage(self.config)
        self.chat_service = None
        self.revision_prompt_folder = None
        self.past_game_status = None        
        self.revision_id = None
        self.make_llm_calls = True
        
    async def pre_process_file(self, file_name, file_path, revision_id):
        # copy files from 
        pass

    async def run_event_from_pre_processed_file(self, event_type, identifier, file_name, revision_id, agents: List[Agent]):        
        # Get payload file from the file system
        file_path = get_path_from_namespace_with_fallback("sample_data")
        file_contents = await self.fs.read_file(file_name=file_name, file_path=file_path)        
        json_object = json.loads(file_contents)

        # Need to put flow into the test data object
        self.chat_service = ChatService(
            chat_service_type="multi_agent",
            chat_history_repository=ingen_deps.get_chat_history_repository(),
            conversation_flow="bike_insights",
            config=self.config
        )
                
        self.revision_id = revision_id
                
        # check if prompt folder is in local_files and if not copy the files from the template folder
        self.revision_prompt_folder = f"prompts/{self.revision_id}"
        file_check = await self.fs.list_files(file_path=self.revision_prompt_folder)
        if file_check is None:
            for file in os.listdir(get_path_from_namespace_with_fallback("templates/prompts")):
                # read the file and write it to the local_files
                with open(f"{get_path_from_namespace_with_fallback("templates/prompts")}{file}", "r") as f:
                    content = f.read()
                    await self.fs.write_file(content, file, self.revision_prompt_folder)

        print(f"Processing {file_name}")

        #thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        json_object["identifier"] = identifier
        json_object["revision_id"] = revision_id
        if self.make_llm_calls:
            chat_request = ChatRequest(
                thread_id=identifier,
                user_prompt=jsonpickle.dumps(json_object, unpicklable=False),
                conversation_flow="ca_insights",
                event_type=event_type
            )

            response = await self.chat_service.get_chat_response(chat_request)
        
            print(response)