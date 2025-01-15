import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import pyodbc
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import json
import ingenious.config.config as ingen_config
from ingenious.utils.load_sample_data import sqlite_sample_db
_config = ingen_config.get_config()


class ToolFunctions:
    @staticmethod
    def aisearch(search_query: str, index_name: str) -> str:
        credential = AzureKeyCredential(_config.azure_search_services[0].key)
        client = SearchClient(
            endpoint=_config.azure_search_services[0].endpoint,
            index_name=index_name,
            credential=credential,
        )
        results = client.search(search_text=search_query, top=5,
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
