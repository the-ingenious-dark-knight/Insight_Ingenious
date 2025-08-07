import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from azure.cosmos import CosmosClient, PartitionKey, exceptions

from ingenious.config.settings import IngeniousSettings
from ingenious.core.structured_logging import get_logger
from ingenious.db.chat_history_repository import IChatHistoryRepository
from ingenious.models.message import Message

logger = get_logger(__name__)


class cosmos_ChatHistoryRepository(IChatHistoryRepository):
    def __init__(self, config: IngeniousSettings):
        connection_string = config.chat_history.database_connection_string
        print(f"Connection string: {connection_string}")
        database_name = config.chat_history.database_name
        print(f"Database name: {database_name}")
        cosmos_client = CosmosClient.from_connection_string(connection_string)
        database_client = cosmos_client.get_database_client(database_name)
        self.container = database_client.create_container_if_not_exists(
            id="chat_history", partition_key=PartitionKey(path="/thread_id")
        )

        self.container_memory = database_client.create_container_if_not_exists(
            id="chat_history_memory", partition_key=PartitionKey(path="/thread_id")
        )

    async def add_message(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()
        message_dict = message.model_dump(mode="json")
        message_dict["id"] = message.message_id
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
        parameters: List[Dict[str, Any]] = [{"name": "@thread_id", "value": thread_id}]
        items = list(
            self.container.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )
        return [Message(**item) for item in items]

    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        item = self.container.read_item(item=message_id, partition_key=thread_id)
        item["positive_feedback"] = positive_feedback
        self.container.replace_item(item=item, body=item)

    async def update_message_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        item = self.container.read_item(item=message_id, partition_key=thread_id)
        item["content_filter_results"] = content_filter_results
        self.container.replace_item(item=item, body=item)

    async def delete_thread(self, thread_id: str) -> None:
        query = "SELECT * FROM c WHERE c.thread_id = @thread_id"
        parameters: List[Dict[str, Any]] = [{"name": "@thread_id", "value": thread_id}]
        items = list(
            self.container.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )
        for item in items:
            self.container.delete_item(item=item["id"], partition_key=item["id"])

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        # Cosmos implementation for update_thread
        logger.info(
            "Updating thread in Cosmos DB",
            thread_id=thread_id,
            user_id=user_id,
            has_name=name is not None,
            has_metadata=metadata is not None,
            operation="update_thread",
        )
        # For now, return the thread_id as this method needs proper implementation
        return thread_id

    async def add_step(
        self, step_dict: IChatHistoryRepository.StepDict
    ) -> IChatHistoryRepository.Step:
        """Add a step to the chat history - simplified implementation for Cosmos DB."""
        # This would need proper implementation for steps support in Cosmos DB

        return IChatHistoryRepository.Step(
            id=UUID(step_dict.get("id", "00000000-0000-0000-0000-000000000000")),
            name=step_dict.get("name", ""),
            type=step_dict.get("type", ""),
            threadId=UUID(
                step_dict.get("threadId", "00000000-0000-0000-0000-000000000000")
            ),
            parentId=UUID(step_dict.get("parentId"))
            if step_dict.get("parentId")
            else None,
            disableFeedback=step_dict.get("disableFeedback", False),
            streaming=step_dict.get("streaming", False),
            waitForAnswer=step_dict.get("waitForAnswer"),
            isError=step_dict.get("isError"),
            metadata=step_dict.get("metadata"),
            tags=step_dict.get("tags"),
            input=step_dict.get("input"),
            output=step_dict.get("output"),
            createdAt=step_dict.get("createdAt"),
            start=step_dict.get("start"),
            end=step_dict.get("end"),
            generation=step_dict.get("generation"),
            showInput=str(step_dict.get("showInput"))
            if step_dict.get("showInput") is not None
            else None,
            language=step_dict.get("language"),
            indent=step_dict.get("indent"),
        )

    async def add_user(
        self, identifier: str, metadata: dict[str, object] | None = None
    ) -> IChatHistoryRepository.User:
        if metadata is None:
            metadata = {}
        user_id = uuid.uuid4()
        user_data = {
            "id": str(user_id),
            "identifier": identifier,
            "createdAt": datetime.now().isoformat(),
            "metadata": metadata,
        }
        self.container.create_item(body=user_data)
        return IChatHistoryRepository.User(
            id=user_id,
            identifier=identifier,
            createdAt=user_data["createdAt"],
            metadata=user_data["metadata"],
        )

    async def get_user(self, identifier: str) -> IChatHistoryRepository.User | None:
        query = "SELECT * FROM c WHERE c.identifier = @identifier"
        parameters: List[Dict[str, Any]] = [
            {"name": "@identifier", "value": identifier}
        ]
        results = list(
            self.container.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )
        if results:
            user_data = results[0]
            return IChatHistoryRepository.User(
                id=user_data["id"],
                identifier=user_data["identifier"],
                createdAt=user_data["createdAt"],
                metadata=user_data.get("metadata", {}),
            )
        return None

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str]
    ) -> Optional[List[IChatHistoryRepository.ThreadDict]]:
        """Retrieve threads associated with a specific user."""
        query = "SELECT * FROM c WHERE c.user_id = @user_id"
        parameters: List[Dict[str, Any]] = [{"name": "@user_id", "value": identifier}]
        if thread_id:
            query += " AND c.thread_id = @thread_id"
            parameters.append({"name": "@thread_id", "value": thread_id})

        results = list(
            self.container.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )

        # Convert results to ThreadDict format - simplified implementation
        if results:
            thread_dicts = []
            for result in results:
                thread_dict: IChatHistoryRepository.ThreadDict = {
                    "id": result.get("thread_id", ""),
                    "createdAt": result.get("timestamp", ""),
                    "name": result.get("name"),
                    "userId": result.get("user_id"),
                    "userIdentifier": identifier,
                    "tags": result.get("tags"),
                    "metadata": result.get("metadata"),
                    "steps": [],
                    "elements": [],
                }
                thread_dicts.append(thread_dict)
            return thread_dicts
        return None

    async def add_memory(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()

        # Prepare message dictionary for insertion
        message_dict = {
            "id": message.message_id,
            "user_id": message.user_id,
            "thread_id": message.thread_id,
            "message_id": message.message_id,
            "positive_feedback": message.positive_feedback,
            "timestamp": message.timestamp.isoformat(),
            "role": message.role,
            "content": message.content,
            "content_filter_results": message.content_filter_results,
            "tool_calls": message.tool_calls,
            "tool_call_id": message.tool_call_id,
            "tool_call_function": message.tool_call_function,
            "is_memory": True,  # Flag to indicate that this is a memory entry
        }

        # Insert the memory record into CosmosDB
        try:
            self.container_memory.create_item(body=message_dict)
        except exceptions.CosmosHttpResponseError as e:
            raise RuntimeError(f"Failed to add memory to CosmosDB: {e}")

        return message.message_id

    async def get_memory(self, message_id: str, thread_id: str) -> Message | None:
        try:
            query = """
                SELECT * FROM c WHERE c.thread_id = @thread_id
                AND c.message_id = @message_id AND c.is_memory = true
                ORDER BY c.timestamp DESC
                OFFSET 0 LIMIT 1
            """
            parameters: List[Dict[str, Any]] = [
                {"name": "@thread_id", "value": thread_id},
                {"name": "@message_id", "value": message_id},
            ]
            items = list(
                self.container_memory.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True,
                )
            )
            if items:
                return Message(**items[0])
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                return None
            raise

    async def update_memory(self) -> None:
        # Query to find the latest record for each thread
        query = """
            SELECT c.user_id, c.thread_id, c.message_id, c.positive_feedback, c.timestamp,
                   c.role, c.content, c.content_filter_results, c.tool_calls,
                   c.tool_call_id, c.tool_call_function
            FROM c
            WHERE c.is_memory = true
            ORDER BY c.thread_id, c.timestamp DESC
        """

        # Retrieve the latest memory records from CosmosDB
        items = list(
            self.container_memory.query_items(
                query=query, enable_cross_partition_query=True
            )
        )
        latest_records = {}

        # Deduplicate by thread_id, keeping only the latest record
        for item in items:
            thread_id = item["thread_id"]
            if thread_id not in latest_records:
                latest_records[thread_id] = item

        # Delete all memory records
        delete_query = "SELECT c.id FROM c WHERE c.is_memory = true"
        delete_items = list(
            self.container_memory.query_items(
                query=delete_query, enable_cross_partition_query=True
            )
        )
        for item in delete_items:
            self.container_memory.delete_item(
                item=item["id"], partition_key=item["thread_id"]
            )

        # Insert the latest memory records back into CosmosDB
        for record in latest_records.values():
            try:
                self.container_memory.create_item(body=record)
            except exceptions.CosmosHttpResponseError as e:
                raise RuntimeError(f"Failed to update memory in CosmosDB: {e}")

    async def get_thread_memory(self, thread_id: str) -> list[Message]:
        query = """
            SELECT * FROM c WHERE c.thread_id = @thread_id
            AND c.is_memory = true ORDER BY c.timestamp DESC
        """
        parameters: List[Dict[str, Any]] = [{"name": "@thread_id", "value": thread_id}]
        items = list(
            self.container_memory.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )
        return [Message(**item) for item in items] if items else []

    async def update_memory_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        try:
            # Retrieve the memory record
            item = self.container_memory.read_item(
                item=message_id, partition_key=thread_id
            )
            if item.get("is_memory"):
                # Update the positive_feedback field
                item["positive_feedback"] = positive_feedback
                self.container_memory.replace_item(item=item, body=item)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                raise ValueError("Memory not found")
            raise

    async def update_memory_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        try:
            # Retrieve the memory record
            item = self.container_memory.read_item(
                item=message_id, partition_key=thread_id
            )
            if item.get("is_memory"):
                # Update the content_filter_results field
                item["content_filter_results"] = content_filter_results
                self.container_memory.replace_item(item=item, body=item)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                raise ValueError("Memory not found")
            raise

    async def delete_thread_memory(self, thread_id: str) -> None:
        # Query to find all memory records for the thread
        query = (
            "SELECT c.id FROM c WHERE c.thread_id = @thread_id AND c.is_memory = true"
        )
        parameters: List[Dict[str, Any]] = [{"name": "@thread_id", "value": thread_id}]
        items = list(
            self.container_memory.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )

        # Delete each memory record found
        for item in items:
            self.container_memory.delete_item(item=item["id"], partition_key=thread_id)

    async def delete_user_memory(self, user_id: str) -> None:
        # Query to find all memory records for the user
        query = "SELECT c.id FROM c WHERE c.user_id = @user_id AND c.is_memory = true"
        parameters: List[Dict[str, Any]] = [{"name": "@user_id", "value": user_id}]
        items = list(
            self.container_memory.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )

        # Delete each memory record found
        for item in items:
            self.container_memory.delete_item(item=item["id"], partition_key=user_id)
