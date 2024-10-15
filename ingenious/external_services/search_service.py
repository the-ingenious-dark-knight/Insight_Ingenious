import logging
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

logger = logging.getLogger(__name__)


class AzureSearchService:
    def __init__(
        self,
        endpoint: str,
        key: str,
        index_name: str = "default-index"
    ):
        self.endpoint = endpoint
        self.key = key
        self.index_name = index_name
        self.credential = AzureKeyCredential(self.key)
        self.client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )

    async def search(self, query, top=5) -> list[dict]:
        try:
            results = self.client.search(search_text=query, top=top)
            return [dict(result) for result in results]
        except Exception as e:
            logger.exception(e)
            return []

    async def suggest(self, query, top=5) -> list[dict]:
        try:
            results = self.client.suggest(search_text=query, suggester_name="sg", top=top)
            return [dict(result) for result in results]
        except Exception as e:
            logger.exception(e)
            return []
