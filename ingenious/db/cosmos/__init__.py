from datetime import datetime
from typing import Dict, List, Optional
import uuid
import os
from azure.cosmos import DatabaseProxy, PartitionKey, exceptions, CosmosClient, DatabaseProxy
from ingenious.models.message import Message
from ingenious.db.chat_history_repository import IChatHistoryRepository
import ingenious.config.config as Config


class cosmos_ChatHistoryRepository(IChatHistoryRepository):
    def __init__(self, config: Config.Config):
        connection_string = config.chat_history.database_connection_string
        print(f"Connection string: {connection_string}")
        database_name = config.chat_history.database_name
        print(f"Database name: {database_name}")
        cosmos_client = CosmosClient.from_connection_string(connection_string)
        database_client = cosmos_client.get_database_client(database_name)
        self.container = database_client.create_container_if_not_exists(
            id="chat_history",
            partition_key=PartitionKey(path="/thread_id")
        )

    async def add_message(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()
        message_dict = message.model_dump(mode="json")
        message_dict['id'] = message.message_id
        self.container.create_item(body=message_dict)

        return message.message_id

    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        try:
            item = self.container.read_item(item=message_id, partition_key=thread_id)
            return Message(**item)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                return None
            raise

    async def get_thread_messages(self, thread_id: str) -> list[Message]:
        query = "SELECT * FROM c WHERE c.thread_id = @thread_id ORDER BY c.timestamp"
        parameters: list[dict[str, object]] = [{"name": "@thread_id", "value": thread_id}]
        items = list(self.container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
        return [Message(**item) for item in items]

    async def update_message_feedback(self, message_id: str, thread_id: str, positive_feedback: bool | None) -> None:
        item = self.container.read_item(item=message_id, partition_key=thread_id)
        item['positive_feedback'] = positive_feedback
        self.container.replace_item(item=item, body=item)

    async def update_message_content_filter_results(
            self, message_id: str, thread_id: str, content_filter_results: dict[str, object]) -> None:
        item = self.container.read_item(item=message_id, partition_key=thread_id)
        item['content_filter_results'] = content_filter_results
        self.container.replace_item(item=item, body=item)

    async def delete_thread(self, thread_id: str) -> None:
        query = "SELECT * FROM c WHERE c.thread_id = @thread_id"
        parameters: list[dict[str, object]] = [{"name": "@thread_id", "value": thread_id}]
        items = list(self.container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
        for item in items:
            self.container.delete_item(item=item['id'], partition_key=item['id'])

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        pass
    
    async def add_user(self, identifier: str) -> IChatHistoryRepository.User:
        """ adds a user to the chat history database """
        pass

    async def get_user(self, identifier: str) -> IChatHistoryRepository.User | None:
        """ gets a user from the chat history database """
        pass
    
    async def get_memory(self, message_id: str, thread_id: str) -> Optional[Message]:
        """Retrieve memory associated with a specific message."""
        try:
            item = self.container.read_item(item=message_id, partition_key=thread_id)
            return Message(**item)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                return None
            raise

    async def update_sql_memory(self) -> Optional[Message]:
        """Update SQL-based memory storage."""
        # Implement the logic to update SQL-based memory here
        pass

    async def get_thread_memory(self, thread_id: str) -> Optional[List[Message]]:
        """Retrieve memory associated with a thread."""
        query = "SELECT * FROM c WHERE c.thread_id = @thread_id ORDER BY c.timestamp"
        parameters = [{"name": "@thread_id", "value": thread_id}]
        results = list(self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        return [Message(**result) for result in results] if results else None

    async def get_threads_for_user(self, identifier: str, thread_id: Optional[str]) -> Optional[List[Dict]]:
        """Retrieve threads associated with a specific user."""
        query = "SELECT * FROM c WHERE c.user_id = @user_id"
        parameters = [{"name": "@user_id", "value": identifier}]
        if thread_id:
            query += " AND c.thread_id = @thread_id"
            parameters.append({"name": "@thread_id", "value": thread_id})

        results = list(self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        return results if results else None

    async def update_memory_feedback(self, message_id: str, thread_id: str, positive_feedback: bool) -> None:
        """Update feedback for memory."""
        await self.update_message_feedback(message_id, thread_id, positive_feedback)

    async def update_memory_content_filter_results(self, message_id: str, thread_id: str, content_filter_results: Dict[str, object]) -> None:
        """Update content filtering results for memory."""
        await self.update_message_content_filter_results(message_id, thread_id, content_filter_results)

    async def delete_thread_memory(self, thread_id: str) -> None:
        """Delete memory associated with a thread."""
        await self.delete_thread(thread_id)
   