from datetime import datetime
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
