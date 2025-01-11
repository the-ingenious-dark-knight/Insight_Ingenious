import json
import logging
import os
from datetime import datetime
from pathlib import Path
import autogen
import autogen.runtime_logging
from jinja2 import Environment, FileSystemLoader

import ingenious.config.config as config
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback
from ingenious_extensions.services.chat_services.multi_agent.conversation_patterns.pet_insights.pet_insights import \
    ConversationPattern

logger = logging.getLogger(__name__)


def maintain_memory(file_path, new_content, max_words=150):
    # Read the current content if the file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as memory_file:
            current_content = memory_file.read()
    else:
        current_content = ""

    # Combine the current content and the new content
    combined_content = current_content + " " + new_content
    words = combined_content.split()

    # Keep only the last `max_words` words
    truncated_content = " ".join(words[-max_words:])

    # Write the truncated content back to the file
    with open(file_path, "w") as memory_file:
        memory_file.write(truncated_content)


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(
            message: str,
            thread_memory: str = '',
            memory_record_switch=True,
            thread_chat_history: list = []
    ) -> tuple[str, str]:

        _config = config.get_config()
        llm_config = _config.models[0].__dict__

        # quick local memory
        memory_path = _config.chat_history.memory_path
        file_path = f"{memory_path}/context.md"

        _classification_agent_pattern = ConversationPattern(default_llm_config=llm_config,
                                                            topics=['sample'],
                                                            memory_record_switch=True,
                                                            memory_path=memory_path,
                                                            thread_memory='')

        ################################################################################################################
        # Load Jinja environment for prompts
        template_path = get_path_from_namespace_with_fallback(str(Path("templates")/Path("prompts")))
        logger.debug(f"Loading templates from: {template_path}")
        env = Environment(loader=FileSystemLoader(template_path), autoescape=True)

        ################################################################################################################
        # Render system prompt

        # Get appropriate prompt template based on event_type
        for sub_agent in ['sample']:
            template_name = f"{sub_agent}_prompt.jinja" if sub_agent else "undefined_prompt.jinja"
            template = env.get_template(template_name)
            system_prompt = template.render(topic=sub_agent)
            topic_agent = autogen.AssistantAgent(
                name=  "agent_" + sub_agent,
                system_message=system_prompt,
                description=f"I focus solely on insights on {sub_agent}.",
                llm_config=llm_config,
            )
            _classification_agent_pattern.add_topic_agent(topic_agent)


        res, memory_summary = await _classification_agent_pattern.get_conversation_response(message)
        maintain_memory(file_path, res)


        return res, memory_summary
