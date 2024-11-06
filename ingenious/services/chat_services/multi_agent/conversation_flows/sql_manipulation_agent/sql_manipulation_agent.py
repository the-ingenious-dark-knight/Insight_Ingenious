import autogen
import autogen.retrieve_utils
import autogen.runtime_logging

import ingenious.config.config as config
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.conversation_patterns.sql_manipulation_agent.sql_manipulation_agent import \
    ConversationPattern
from ingenious.services.chat_services.multi_agent.tool_factory import SQL_ToolFunctions, PandasExecutor
import pandas as pd

class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str, topics: list = [], thread_memory: str = '',
                                        memory_record_switch=True,
                                        thread_chat_history: list[str, str] = []) -> ChatResponse:
        _config = config.get_config()
        llm_config = _config.models[0].__dict__
        memory_path = _config.chat_history.memory_path

        # Initialize the knowledge base agent pattern, you only need to add defined topics here
        agent_pattern = ConversationPattern(default_llm_config=llm_config,
                                            topics=topics,
                                            memory_record_switch=memory_record_switch,
                                            memory_path=memory_path,
                                            thread_memory=thread_memory)

        if _config.azure_sql_services.database_name == 'skip':

            table_name, column_names = SQL_ToolFunctions.get_db_attr(_config) #enable this for local sql
            sql_writer = autogen.AssistantAgent(
                "sql_writer",
                llm_config=llm_config,
                system_message=(
                    f"""
                        - You are skilled in writing SQL queries. Always respond by calling `sql_query_tool`
                          with a SQL query formatted as "SELECT ... FROM {table_name}", including grouping or aggregation as needed.
                        - The target table contains the following columns: {", ".join(column_names)}.
                        - Format your output based on the number of rows:
                          - **Single Row**: Use the format `{{column_name: value, column_name: value}}`.
                          - **Multiple Rows**: Use a list format with each row as a dictionary, e.g., `[{{column_name: value}}, {{column_name: value}}]`.
                        """),
                description=("""I am **ONLY** allowed to speak **immediately** after `researcher`."""),
                is_termination_msg=agent_pattern.termination_msg,
            )

            agent_pattern.sql_writer = sql_writer
            autogen.register_function(
                SQL_ToolFunctions.execute_sql_local,
                caller=agent_pattern.sql_writer,
                executor=agent_pattern.researcher,
                name="sql_query_tool",
                description="Use this tool to perform sql query."
            )

        else:

            database_name, table_name, column_names = SQL_ToolFunctions.get_azure_db_attr(_config) #enable this for azure sql
            sql_writer = autogen.AssistantAgent(
                "sql_writer",
                llm_config=llm_config,
                system_message=(
                    f"""
                        - You are skilled in writing SQL queries. Always respond by calling `sql_query_tool` 
                          with a SQL query formatted as "SELECT ... FROM {database_name}.{table_name}", including grouping or aggregation as needed.
                        - The target table contains the following columns: {", ".join(column_names)}.
                        - Format your output based on the number of rows:
                          - **Single Row**: Use the format `{{column_name: value, column_name: value}}`.
                          - **Multiple Rows**: Use a list format with each row as a dictionary, e.g., `[{{column_name: value}}, {{column_name: value}}]`.
                        """),
                description=("""I am **ONLY** allowed to speak **immediately** after `researcher`."""),
                is_termination_msg=agent_pattern.termination_msg,
            )

            agent_pattern.sql_writer = sql_writer
            autogen.register_function(
                SQL_ToolFunctions.execute_sql_azure,
                caller=agent_pattern.sql_writer,
                executor=agent_pattern.researcher,
                name="sql_query_tool",
                description="Use this tool to perform sql query."
            )


        agent_pattern.analyst_agent = autogen.AssistantAgent(
            name="analyst",
            system_message=("Check if the result makes sense in mathematics, "
                            "if yes, return 'Please compose the final result.'"
                            "if no, return 'The query result need to be examined.'"),
            description="I am **ONLY** allowed to respond **immediately** after `researcher`.",
            llm_config=llm_config,
            is_termination_msg=agent_pattern.termination_msg,
        )


        # agent_pattern.analyst_agent = analyst_agent
        # autogen.register_function(
        #     PandasExecutor.plot_bar_chart,
        #     caller=agent_pattern.analyst_agent,
        #     executor=agent_pattern.researcher,
        #     name="matplotlib_tool",
        #     description="Use this tool to perform analysis and visualisation with matplotlib."
        # )


        # Get the conversation response using the pattern
        res, memory_summary = await agent_pattern.get_conversation_response(message)
        return res, memory_summary
