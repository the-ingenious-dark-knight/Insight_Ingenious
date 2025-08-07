from typing import Any, Dict, List, Optional

from ingenious.config.settings import IngeniousSettings
from ingenious.db.base_sql import BaseSQLRepository
from ingenious.db.chat_history_repository import IChatHistoryRepository
from ingenious.db.connection_pool import (
    AzureSQLConnectionFactory,
    ConnectionPool,
    SQLiteConnectionFactory,
)
from ingenious.db.query_builder import (
    AzureSQLDialect,
    CosmosDialect,
    QueryBuilder,
    SQLiteDialect,
)
from ingenious.models.database_client import DatabaseClientType


class RepositoryFactory:
    """Factory for creating database repository instances based on configuration."""

    @staticmethod
    def create_chat_history_repository(
        db_type: DatabaseClientType, config: IngeniousSettings
    ) -> IChatHistoryRepository:
        """Create a chat history repository based on database type."""

        if db_type == DatabaseClientType.SQLITE:
            return RepositoryFactory._create_sqlite_repository(config)
        elif db_type == DatabaseClientType.AZURESQL:
            return RepositoryFactory._create_azuresql_repository(config)
        elif db_type == DatabaseClientType.COSMOS:
            from ingenious.db.cosmos import cosmos_ChatHistoryRepository

            return cosmos_ChatHistoryRepository(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def _create_sqlite_repository(config: IngeniousSettings) -> IChatHistoryRepository:
        """Create SQLite repository with proper dependencies."""
        from ingenious.db.sqlite import sqlite_ChatHistoryRepository

        return sqlite_ChatHistoryRepository(config)

    @staticmethod
    def _create_azuresql_repository(
        config: IngeniousSettings,
    ) -> IChatHistoryRepository:
        """Create Azure SQL repository with proper dependencies."""
        from ingenious.db.azuresql import azuresql_ChatHistoryRepository

        return azuresql_ChatHistoryRepository(config)

    @staticmethod
    def _create_cosmos_repository(config: IngeniousSettings) -> IChatHistoryRepository:
        """Create Cosmos DB repository with proper dependencies."""
        from ingenious.db.cosmos import cosmos_ChatHistoryRepository

        return cosmos_ChatHistoryRepository(config)


class ModernRepositoryFactory:
    """Modern factory that creates repositories using composition pattern directly."""

    @staticmethod
    def create_chat_history_repository(
        db_type: DatabaseClientType, config: IngeniousSettings
    ) -> IChatHistoryRepository:
        """Create a repository using composition pattern."""

        if db_type == DatabaseClientType.SQLITE:
            return ModernRepositoryFactory._create_sqlite_repository(config)
        elif db_type == DatabaseClientType.AZURESQL:
            return ModernRepositoryFactory._create_azuresql_repository(config)
        elif db_type == DatabaseClientType.COSMOS:
            return ModernRepositoryFactory._create_cosmos_repository(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def _create_sqlite_repository(
        config: IngeniousSettings,
    ) -> "SQLiteChatHistoryRepository":
        """Create SQLite repository using composition."""
        import os

        db_path = config.chat_history.database_path

        # Ensure directory exists
        db_dir_check = os.path.dirname(db_path)
        if not os.path.exists(db_dir_check):
            os.makedirs(db_dir_check)

        # Create dependencies
        connection_factory = SQLiteConnectionFactory(db_path)
        pool_size = getattr(config.chat_history, "connection_pool_size", 8)
        connection_pool = ConnectionPool(connection_factory, pool_size=pool_size)
        query_builder = QueryBuilder(SQLiteDialect())

        return SQLiteChatHistoryRepository(config, query_builder, connection_pool)

    @staticmethod
    def _create_azuresql_repository(
        config: IngeniousSettings,
    ) -> "AzureSQLChatHistoryRepository":
        """Create Azure SQL repository using composition."""
        connection_string = config.chat_history.database_connection_string
        if not connection_string:
            raise ValueError(
                "Azure SQL connection string is required for azuresql chat history repository"
            )

        # Create dependencies
        connection_factory = AzureSQLConnectionFactory(connection_string)
        pool_size = getattr(config.chat_history, "connection_pool_size", 8)
        connection_pool = ConnectionPool(connection_factory, pool_size=pool_size)
        query_builder = QueryBuilder(AzureSQLDialect())

        return AzureSQLChatHistoryRepository(config, query_builder, connection_pool)

    @staticmethod
    def _create_cosmos_repository(
        config: IngeniousSettings,
    ) -> "CosmosChatHistoryRepository":
        """Create Cosmos DB repository using composition."""
        # Cosmos DB doesn't use traditional connection pooling like SQL databases
        # Instead, it uses the Azure Cosmos SDK directly for connection management
        query_builder = QueryBuilder(CosmosDialect())

        return CosmosChatHistoryRepository(config, query_builder)


class SQLiteChatHistoryRepository(BaseSQLRepository):
    """Modern SQLite repository using composition."""

    def __init__(
        self,
        config: IngeniousSettings,
        query_builder: QueryBuilder,
        connection_pool: ConnectionPool,
    ):
        self.pool = connection_pool
        super().__init__(config, query_builder)

    def __del__(self) -> None:
        """Destructor to ensure connections are properly closed."""
        try:
            self.close()
        except Exception:
            pass

    def close(self) -> None:
        """Close all connections in the pool."""
        if hasattr(self, "pool"):
            self.pool.close_all()

    def _init_connection(self) -> None:
        """Connection already initialized via connection pool."""
        pass

    def _execute_sql(
        self, sql: str, params: list[Any] | None = None, expect_results: bool = True
    ) -> Any:
        """Execute SQL using the connection pool."""
        if params is None:
            params = []

        try:
            with self.pool.get_connection() as connection:
                cursor = connection.cursor()

                if expect_results:
                    res = cursor.execute(sql, params)
                    rows = res.fetchall()
                    result = [dict(row) for row in rows]
                    return result
                else:
                    connection.execute(sql, params)
                    connection.commit()

        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "SQLite query execution failed",
                context={
                    "query_preview": sql[:100] + "..." if len(sql) > 100 else sql,
                    "param_count": len(params) if params else 0,
                    "expect_results": expect_results,
                },
                cause=e,
            ) from e

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str] = None
    ) -> Any:
        """Get threads for user - delegates to existing SQLite implementation."""
        # This would be implemented by copying the existing implementation
        # from the SQLite repository class
        pass

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Update thread - delegates to existing SQLite implementation."""
        # This would be implemented by copying the existing implementation
        # from the SQLite repository class
        return ""


class AzureSQLChatHistoryRepository(BaseSQLRepository):
    """Modern Azure SQL repository using composition."""

    def __init__(
        self,
        config: IngeniousSettings,
        query_builder: QueryBuilder,
        connection_pool: ConnectionPool,
    ):
        self.pool = connection_pool
        super().__init__(config, query_builder)

    def _init_connection(self) -> None:
        """Connection already initialized via connection pool."""
        pass

    def _execute_sql(
        self, sql: str, params: list[Any] | None = None, expect_results: bool = True
    ) -> Any:
        """Execute SQL using the connection pool."""
        if params is None:
            params = []

        try:
            with self.pool.get_connection() as connection:
                cursor = connection.cursor()

                if expect_results:
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    # Convert to list of dictionaries
                    columns = [column[0] for column in cursor.description]
                    result = [dict(zip(columns, row)) for row in rows]
                    cursor.close()
                    return result
                else:
                    cursor.execute(sql, params)
                    connection.commit()
                    cursor.close()

        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Azure SQL query execution failed",
                context={
                    "query_preview": sql[:100] + "..." if len(sql) > 100 else sql,
                    "param_count": len(params) if params else 0,
                    "expect_results": expect_results,
                },
                cause=e,
            ) from e

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str] = None
    ) -> Any:
        """Get threads for user - delegates to existing Azure SQL implementation."""
        # This would be implemented by copying the existing implementation
        # from the Azure SQL repository class
        pass

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Update thread - delegates to existing Azure SQL implementation."""
        # This would be implemented by copying the existing implementation
        # from the Azure SQL repository class
        return ""


class CosmosChatHistoryRepository(IChatHistoryRepository):
    """Cosmos DB repository using composition pattern with modern factory approach."""

    def __init__(
        self,
        config: IngeniousSettings,
        query_builder: Optional[QueryBuilder] = None,
        connection_pool: Optional[Any] = None,
    ):
        """Initialize Cosmos DB repository with modern composition pattern."""
        from azure.cosmos import CosmosClient, PartitionKey

        self.config = config
        self.query_builder = query_builder  # Available for future Cosmos query building
        # Note: connection_pool is not used for Cosmos DB but kept for interface consistency

        # Initialize Cosmos DB client
        connection_string = config.chat_history.database_connection_string
        database_name = config.chat_history.database_name

        if not connection_string:
            raise ValueError("Cosmos DB connection string is required")
        if not database_name:
            raise ValueError("Cosmos DB database name is required")

        self.cosmos_client = CosmosClient.from_connection_string(connection_string)
        self.database_client = self.cosmos_client.get_database_client(database_name)

        # Create containers if they don't exist
        self.container = self.database_client.create_container_if_not_exists(
            id="chat_history", partition_key=PartitionKey(path="/thread_id")
        )
        self.container_memory = self.database_client.create_container_if_not_exists(
            id="chat_history_memory", partition_key=PartitionKey(path="/thread_id")
        )

    # Implement IChatHistoryRepository interface methods
    async def add_message(self, message) -> str:
        """Add a message to Cosmos DB."""
        import uuid
        from datetime import datetime

        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()
        message_dict = message.model_dump(mode="json")
        message_dict["id"] = message.message_id

        try:
            self.container.create_item(body=message_dict)
            return message.message_id
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to add message to Cosmos DB",
                context={
                    "message_id": message.message_id,
                    "thread_id": message.thread_id,
                },
                cause=e,
            ) from e

    async def get_message(self, message_id: str, thread_id: str):
        """Retrieve a message from Cosmos DB."""
        from azure.cosmos import exceptions

        try:
            item = self.container.read_item(item=message_id, partition_key=thread_id)
            from ingenious.models.message import Message

            return Message(**item)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                return None
            raise

    async def get_thread_messages(self, thread_id: str):
        """Get all messages for a thread."""
        query = "SELECT * FROM c WHERE c.thread_id = @thread_id ORDER BY c.timestamp"
        parameters: List[Dict[str, Any]] = [{"name": "@thread_id", "value": thread_id}]

        try:
            items = list(
                self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True,
                )
            )
            from ingenious.models.message import Message

            return [Message(**item) for item in items]
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to retrieve thread messages from Cosmos DB",
                context={"thread_id": thread_id},
                cause=e,
            ) from e

    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        """Update message feedback in Cosmos DB."""
        try:
            item = self.container.read_item(item=message_id, partition_key=thread_id)
            item["positive_feedback"] = positive_feedback
            self.container.replace_item(item=item, body=item)
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to update message feedback in Cosmos DB",
                context={"message_id": message_id, "thread_id": thread_id},
                cause=e,
            ) from e

    async def update_message_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        """Update message content filter results in Cosmos DB."""
        try:
            item = self.container.read_item(item=message_id, partition_key=thread_id)
            item["content_filter_results"] = content_filter_results
            self.container.replace_item(item=item, body=item)
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to update message content filter results in Cosmos DB",
                context={"message_id": message_id, "thread_id": thread_id},
                cause=e,
            ) from e

    async def delete_thread(self, thread_id: str) -> None:
        """Delete all messages in a thread from Cosmos DB."""
        query = "SELECT * FROM c WHERE c.thread_id = @thread_id"
        parameters: List[Dict[str, Any]] = [{"name": "@thread_id", "value": thread_id}]

        try:
            items = list(
                self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True,
                )
            )
            for item in items:
                self.container.delete_item(
                    item=item["id"], partition_key=item["thread_id"]
                )
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to delete thread from Cosmos DB",
                context={"thread_id": thread_id},
                cause=e,
            ) from e

    async def add_user(
        self, identifier: str, metadata: dict[str, object] | None = None
    ):
        """Add a user to Cosmos DB."""
        import uuid
        from datetime import datetime

        if metadata is None:
            metadata = {}

        user_id = uuid.uuid4()
        user_data = {
            "id": str(user_id),
            "identifier": identifier,
            "createdAt": datetime.now().isoformat(),
            "metadata": metadata,
            "thread_id": str(user_id),  # Use user_id as partition key
        }

        try:
            self.container.create_item(body=user_data)
            return IChatHistoryRepository.User(
                id=user_id,
                identifier=identifier,
                createdAt=user_data["createdAt"],
                metadata=metadata,
            )
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to add user to Cosmos DB",
                context={"identifier": identifier},
                cause=e,
            ) from e

    async def get_user(self, identifier: str):
        """Get a user from Cosmos DB."""
        query = "SELECT * FROM c WHERE c.identifier = @identifier"
        parameters: List[Dict[str, Any]] = [
            {"name": "@identifier", "value": identifier}
        ]

        try:
            results = list(
                self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True,
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
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to get user from Cosmos DB",
                context={"identifier": identifier},
                cause=e,
            ) from e

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str] = None
    ):
        """Get threads for a user from Cosmos DB."""
        query = "SELECT * FROM c WHERE c.user_id = @user_id"
        parameters: List[Dict[str, Any]] = [{"name": "@user_id", "value": identifier}]

        if thread_id:
            query += " AND c.thread_id = @thread_id"
            parameters.append({"name": "@thread_id", "value": thread_id})

        try:
            results = list(
                self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True,
                )
            )

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
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to get threads for user from Cosmos DB",
                context={"identifier": identifier, "thread_id": thread_id},
                cause=e,
            ) from e

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Update thread in Cosmos DB."""
        from ingenious.core.structured_logging import get_logger

        logger = get_logger(__name__)
        logger.info(
            "Updating thread in Cosmos DB",
            thread_id=thread_id,
            user_id=user_id,
            has_name=name is not None,
            has_metadata=metadata is not None,
            operation="update_thread",
        )

        # For this implementation, we return the thread_id
        # In a full implementation, you would update the thread document
        return thread_id

    async def add_step(self, step_dict) -> IChatHistoryRepository.Step:
        """Add a step to Cosmos DB."""
        from uuid import UUID

        # Simplified step implementation for Cosmos DB
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

    # Memory operations for Cosmos DB
    async def add_memory(self, message) -> str:
        """Add a memory message to Cosmos DB."""
        import uuid
        from datetime import datetime

        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()

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
            "is_memory": True,
        }

        try:
            self.container_memory.create_item(body=message_dict)
            return message.message_id
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to add memory to Cosmos DB",
                context={
                    "message_id": message.message_id,
                    "thread_id": message.thread_id,
                },
                cause=e,
            ) from e

    async def get_memory(self, message_id: str, thread_id: str):
        """Get a memory message from Cosmos DB."""
        from azure.cosmos import exceptions

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
                from ingenious.models.message import Message

                return Message(**items[0])
            return None
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                return None
            raise

    async def get_thread_memory(self, thread_id: str):
        """Get all memory messages for a thread from Cosmos DB."""
        query = """
            SELECT * FROM c WHERE c.thread_id = @thread_id
            AND c.is_memory = true ORDER BY c.timestamp DESC
        """
        parameters: List[Dict[str, Any]] = [{"name": "@thread_id", "value": thread_id}]

        try:
            items = list(
                self.container_memory.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True,
                )
            )
            from ingenious.models.message import Message

            return [Message(**item) for item in items] if items else []
        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to get thread memory from Cosmos DB",
                context={"thread_id": thread_id},
                cause=e,
            ) from e

    async def update_memory(self) -> None:
        """Update memory in Cosmos DB (deduplication logic)."""
        # Implementation for memory deduplication similar to existing cosmos repository
        query = """
            SELECT c.user_id, c.thread_id, c.message_id, c.positive_feedback, c.timestamp,
                   c.role, c.content, c.content_filter_results, c.tool_calls,
                   c.tool_call_id, c.tool_call_function
            FROM c
            WHERE c.is_memory = true
            ORDER BY c.thread_id, c.timestamp DESC
        """

        try:
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

            # Insert the latest memory records back
            for record in latest_records.values():
                self.container_memory.create_item(body=record)

        except Exception as e:
            from ingenious.errors import DatabaseQueryError

            raise DatabaseQueryError(
                "Failed to update memory in Cosmos DB",
                context={},
                cause=e,
            ) from e
