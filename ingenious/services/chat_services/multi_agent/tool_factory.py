import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

import ingenious.config.config as config
from ingenious.utils.load_sample_data import sqlite_sample_db


class ToolFunctions:
    @staticmethod
    def aisearch(search: str, index_name: str) -> str:
        _config = config.get_config()
        credential = AzureKeyCredential(_config.azure_search_services[0].key)
        client = SearchClient(
            endpoint=_config.azure_search_services[0].endpoint,
            index_name=index_name,
            credential=credential,
        )
        results = client.search(search_text=search, top=5,
                                query_type="semantic",  # semantic, full or simple
                                query_answer="extractive",
                                query_caption="extractive",
                                vector_queries=None)  # vector_queries can input the query as a vector
        text_results = ""
        title = ""
        for result in results:
            captions = result['@search.captions']
            for caption in captions:
                text_results = text_results + "; " + caption.text
                if 'title' in result:
                    title = result['title']
                else:
                    title = ""
        return text_results

    @staticmethod
    def update_memory(context: str) -> None:
        _config = config.get_config()
        memory_path = _config.chat_history.memory_path
        with open(f"{memory_path}/context.md", "w") as memory_file:
            memory_file.write(context)


class PandasExecutor:
    @staticmethod
    def plot_bar_chart(data: Dict[str, int]) -> str:
        """
        Generate a bar chart from a dictionary input.

        Parameters:
        data (Dict[str, int]): A dictionary where keys are categories and values are quantities.

        Example:
        plot_bar_chart({"GROUP_A": 518, "GROUP_B": 100})
        """
        # Convert the dictionary to a DataFrame for easier plotting
        df = pd.DataFrame(list(data.items()), columns=['Category', 'Value'])

        # Plotting
        plt.figure(figsize=(8, 6))
        plt.bar(df['Category'], df['Value'])
        plt.xlabel('Category')
        plt.ylabel('Value')
        plt.title('Bar Chart')
        plt.show()

        # Save the plot to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.savefig(temp_file.name)
        plt.close()  # Close the figure to release memory
        return temp_file.name




test_db = sqlite_sample_db()

class SQL_ToolFunctions:
    @staticmethod
    def get_db_attr(_config) :
        table_name = _config.local_sql_db.sample_database_name
        result = test_db.execute_sql(f"""SELECT * FROM {table_name} LIMIT 1""")
        column_names = [key for key in result[0]]
        return table_name, column_names

    @staticmethod
    def execute_sql_local(sql: str,
                          timeout: int = 10  # Timeout in seconds
                          ) -> str:

        def run_query(sql: str):
            return test_db.execute_sql(sql)

        with ThreadPoolExecutor() as executor:
            future = executor.submit(run_query, sql)  # Pass 'sql' as an argument
            try:
                # Wait for the query to complete within the specified timeout
                result = future.result(timeout=timeout)
                return result
            except TimeoutError:
                # Handle case where the query execution exceeded the timeout
                return ""
            except Exception as e:
                # Handle any other exceptions that may arise during query execution
                return str(e)