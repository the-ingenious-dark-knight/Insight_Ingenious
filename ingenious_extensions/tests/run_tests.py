import datetime
import json
import os
from pathlib import Path

# Ingenious imports
import ingenious.config.config as ingen_config
import ingenious.dependencies as ingen_deps
from ingenious.files.files_repository import FileStorage
from ingenious.models.chat import ChatRequest
from ingenious.services.chat_service import ChatService
from ingenious.utils.stage_executor import ProgressConsoleWrapper


class RunBatches:
    def __init__(self, progress: ProgressConsoleWrapper, task_id: str = None):
        self.config = ingen_config.get_config()
        self.fs = FileStorage(config=self.config)
        self.progress = progress
        self.task_id = task_id
        self.directory = "example_payload/raw"

    async def run(self):
        try:
            thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            user_prompt = "give me some test message"

            chat_history_repository = ingen_deps.get_chat_history_repository()

            chat_request = ChatRequest(
                thread_id=thread_id,
                user_prompt=user_prompt,
                conversation_flow="pet_insights",
            )

            chat_service = ChatService(
                chat_service_type="multi_agent",
                chat_history_repository=chat_history_repository,
                conversation_flow="pet_insights",
                config=ingen_config.get_config(),
            )

            response = await chat_service.get_chat_response(chat_request)

            response_content = json.loads(
                json.loads(response.agent_response)["response"]["content"]
            )

            await self.fs.write_file(
                contents=val, file_name="output.md", file_path="./"
            )

            self.Llm_Response_To_Markdown(
                response_content, chat_request, file_name, output_path
            )

            self.progress.progress.update(
                task_id=self.task_id,
                description=f"********* Completed {file_name} ********** \n\n",
            )

        except Exception as e:
            await file_data.Delete_New_Ball_Watermark(config=ingen_deps.config)
            raise ValueError(f"Error processing {file_name}: {e}")

        output_path = self.Get_Functional_Tests_Output_Path()
        self.Write_Markdown_Footer(output_path)
        self.Convert_Markdown_Output_To_Html(output_path)

    def Get_Functional_Tests_Output_Path(
        self, flag_generate_new_id: bool = True, flag_generate_new_insights: bool = True
    ):
        if flag_generate_new_id:
            test_run_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = f"./functional_test_outputs/{test_run_id}/responses.md"
        else:
            test_run_id = "sample_id"
            output_path = f"./functional_test_outputs/{test_run_id}/responses.md"
            if os.path.exists(output_path) and flag_generate_new_insights:
                os.remove(output_path)

        os.makedirs(Path(output_path).parent, exist_ok=True)
        return output_path

    def Convert_Markdown_Output_To_Html(self, output_path: str):
        # Convert the Markdown file to HTML
        with open(output_path, "r") as f:
            markdown_content = f.read()
        html_content = markdown.markdown(
            markdown_content,
            extensions=["extra", "md_in_html", "toc", "fenced_code", "codehilite"],
        )

        template_path = Path("templates") / Path("html_pages")
        template_string = get_file_from_namespace_with_fallback(
            str(template_path), "responses_template.html"
        )
        html_content2 = template_string.replace("{{content}}", html_content)

        # Save the HTML content to a file
        html_output_path = output_path.replace(".md", ".html")
        with open(html_output_path, "w") as f:
            f.write(html_content2)
