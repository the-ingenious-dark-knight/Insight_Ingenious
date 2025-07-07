import json
import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

import ingenious.config.config as ingen_config
from ingenious.config.profile import Profiles
from ingenious.utils.load_sample_data import sqlite_sample_db

_config = ingen_config.get_config()

# Get profile configuration for SQL services
_profiles_obj = Profiles._get_profiles()
_profile = None
if _profiles_obj:
    if hasattr(_profiles_obj, 'get_profile'):
        _profile = _profiles_obj.get_profile("dev")  # Use default profile
    elif isinstance(_profiles_obj, list):
        # If profiles is a list, find the profile manually
        for p in _profiles_obj:
            if hasattr(p, 'name') and p.name == "dev":
                _profile = p
                break

# Handle azure_sql_services configuration
if _config.azure_sql_services is not None:
    use_azure_sql = _config.azure_sql_services.database_name != "skip"
elif _profile and hasattr(_profile, 'azure_sql_services') and _profile.azure_sql_services:
    use_azure_sql = _profile.azure_sql_services.database_name != "skip"
else:
    # Default to SQLite mode
    use_azure_sql = False

# Only import pyodbc if we're using Azure SQL
if use_azure_sql:
    try:
        import pyodbc
    except ImportError:
        print("Warning: pyodbc not available for Azure SQL connections")
        pyodbc = None


class ToolFunctions:
    @staticmethod
    def aisearch(search_query: str, index_name: str) -> str:
        credential = AzureKeyCredential(_config.azure_search_services[0].key)
        client = SearchClient(
            endpoint=_config.azure_search_services[0].endpoint,
            index_name=index_name,
            credential=credential,
        )
        results = client.search(
            search_text=search_query,
            top=5,
            query_type="semantic",  # semantic, full or simple
            query_answer="extractive",
            query_caption="extractive",
            vector_queries=None,
        )  # vector_queries can input the query as a vector
        text_results = ""
        for result in results:
            captions = result["@search.captions"]
            for caption in captions:
                text_results = text_results + "; " + caption.text
                # if "title" in result:
                #     title = result["title"]
                # else:
                #     title = ""
        return text_results

    @staticmethod
    def update_memory(context: str) -> None:
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
        df = pd.DataFrame(list(data.items()), columns=["Category", "Value"])

        # Plotting
        plt.figure(figsize=(8, 6))
        plt.bar(df["Category"], df["Value"])
        plt.xlabel("Category")
        plt.ylabel("Value")
        plt.title("Bar Chart")
        plt.show()

        # Save the plot to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.savefig(temp_file.name)
        plt.close()  # Close the figure to release memory
        return temp_file.name


# SQL Tools TODO: need a better way to wrap these functions
def get_conn(_config, _profile):
    if pyodbc is None:
        raise ImportError(
            "pyodbc is required for Azure SQL connections but is not available"
        )
    
    # Get connection string from config or profile
    connection_string = None
    if _config.azure_sql_services and _config.azure_sql_services.database_connection_string:
        connection_string = _config.azure_sql_services.database_connection_string
    elif _profile and hasattr(_profile, 'azure_sql_services') and _profile.azure_sql_services and _profile.azure_sql_services.database_connection_string:
        connection_string = _profile.azure_sql_services.database_connection_string
    
    if not connection_string:
        raise ValueError("No Azure SQL connection string found in config or profile")
    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    return conn, cursor


# Initialize database connections based on configuration
if not use_azure_sql:
    test_db = sqlite_sample_db()  # this is for local sql initialisation
    conn = cursor = None
else:
    test_db = None  # Placeholder for Azure SQL mode
    if pyodbc is not None:
        try:
            conn, cursor = get_conn(_config, _profile)
        except Exception as e:
            print(f"Warning: Azure SQL configured but connection failed: {e}")
            conn = cursor = None
    else:
        print("Warning: Azure SQL configured but pyodbc not available")
        conn = cursor = None


class SQL_ToolFunctions:
    @staticmethod
    def get_db_attr(_config):
        # Check if we're in SQLite mode
        if not use_azure_sql:
            table_name = _config.local_sql_db.sample_database_name
            result = test_db.execute_sql(f"""SELECT * FROM {table_name} LIMIT 1""")
            if result:
                column_names = [key for key in result[0]]
                return table_name, column_names
            else:
                return table_name, []
        else:
            # Azure SQL mode - get from config or profile
            database_name = None
            table_name = None
            
            if _config.azure_sql_services:
                database_name = _config.azure_sql_services.database_name
                table_name = _config.azure_sql_services.table_name
            elif _profile and hasattr(_profile, 'azure_sql_services') and _profile.azure_sql_services:
                database_name = _profile.azure_sql_services.database_name
                table_name = _profile.azure_sql_services.table_name
            
            if cursor and table_name:
                cursor.execute(f"""
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{table_name}'
                """)
                column_names = [row[0] for row in cursor.fetchall()]
                return database_name, table_name, column_names
            else:
                return database_name or "unknown", table_name or "unknown", []

    @staticmethod
    def get_azure_db_attr(_config):
        # Get database attributes from config or profile
        database_name = None
        table_name = None
        
        if _config.azure_sql_services:
            database_name = _config.azure_sql_services.database_name
            table_name = _config.azure_sql_services.table_name
        elif _profile and hasattr(_profile, 'azure_sql_services') and _profile.azure_sql_services:
            database_name = _profile.azure_sql_services.database_name
            table_name = _profile.azure_sql_services.table_name
        
        if cursor and table_name:
            cursor.execute(f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
            """)
            column_names = [row[0] for row in cursor.fetchall()]
            return database_name, table_name, column_names
        else:
            return database_name or "unknown", table_name or "unknown", []

    @staticmethod
    def execute_sql_local(
        sql: str,
        timeout: int = 10,  # Timeout in seconds
    ) -> str:
        def run_query(sql: str):
            return test_db.execute_sql(sql)

        with ThreadPoolExecutor() as executor:
            future = executor.submit(run_query, sql)  # Pass 'sql' as an argument
            try:
                # Wait for the query to complete within the specified timeout
                result = future.result(timeout=timeout)
                return json.dumps(result)
            except TimeoutError:
                # Handle case where the query execution exceeded the timeout
                return json.dumps({"error": "Query timed out", "results": []})
            except Exception as e:
                # Handle any other exceptions that may arise during query execution
                return json.dumps({"error": str(e), "results": []})

    @staticmethod
    def execute_sql_azure(
        sql: str,
        timeout: int = 15,  # Timeout in seconds
    ) -> str:
        def run_query(sql_query):
            try:
                cursor.execute(sql_query)
                r = [
                    dict(
                        (cursor.description[i][0], value) for i, value in enumerate(row)
                    )
                    for row in cursor.fetchall()
                ]
                return json.dumps(r)
            except Exception as query_err:
                return json.dumps({"error": f"Query Error: {query_err}", "results": []})

        # Run query in a separate thread with a timeout
        with ThreadPoolExecutor() as executor:
            future = executor.submit(run_query, sql)
            try:
                result = future.result(timeout=timeout)
                return result
            except TimeoutError:
                return json.dumps({"error": "Query timed out", "results": []})
            except Exception as e:
                return json.dumps({"error": f"Execution Error: {e}", "results": []})
