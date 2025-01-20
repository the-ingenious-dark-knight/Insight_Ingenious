import os
from pathlib import Path
import autogen
import autogen.runtime_logging
from jinja2 import Environment, FileSystemLoader
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback
# Custom class import from ingenious_extensions 
from ingenious.services.chat_services.multi_agent.service import IConversationFlow
from ingenious.ingenious_extensions_template.services.chat_services.multi_agent \
    .conversation_patterns.bike_insights.bike_insights import ConversationPattern


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


class ConversationFlow(IConversationFlow):
    async def get_conversation_response(
            self,
            message: str,
            thread_memory: str = '',
            memory_record_switch=True,
            thread_chat_history: list = []
    ) -> tuple[str, str]:

        # get your llm model from the configuration array
        llm_config = self.Get_Models[0]
        # Note the base IConversationFlow gives you a logger for logging purposes
        self._logger.debug("Starting Flow")
        # You have the option of maintaining reusable logic in a conversation pattern class or you could put all of the logic in this class
        # In this sample case our reusable pattern will be multiple specialist research agents with a summariser at the end
        
        # First we need to instantiate the reusable pattern class
        _classification_agent_pattern = ConversationPattern(default_llm_config=llm_config,
                                                            topics=['sample'],
                                                            memory_record_switch=True,
                                                            memory_path=self._memory_path,
                                                            thread_memory='')

        # Next we will add the specialist topic agents to the pattern. 
        # In another flow, for a different use case, we could re-use the pattern with a different set of topic agents
        for sub_agent in ['customer_sentiment_agent', 'fiscal_analysis_agent']:
            template_name = f"{sub_agent}_prompt.jinja"
            # The abstract class has a built in property which is a jinia2 environment object. 
            # This environment object first searches for prompts 
            # within the ingenious_extensions/templates/prompts/ folder and, 
            # if it cant find this it falls back to the ingenious/templates/prompts/ folder 
            template = self._prompt_template_env.get_template(template_name)
            system_prompt = template.render(topic=sub_agent)
            topic_agent = autogen.AssistantAgent(
                name=sub_agent,
                system_message=system_prompt,
                description=f"I focus solely on {sub_agent}.",
                llm_config=llm_config,
            )
            _classification_agent_pattern.add_topic_agent(topic_agent)

        res, memory_summary = await _classification_agent_pattern.get_conversation_response(message)
        
        # Add this if you want to maintain a local memory file
        self.maintain_memory(res)

        return res, memory_summary
