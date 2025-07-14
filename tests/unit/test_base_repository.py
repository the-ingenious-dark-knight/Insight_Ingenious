import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

import ingenious.config.config as Config
from ingenious.db.base_sql import BaseSQLRepository
from ingenious.db.chat_history_repository import IChatHistoryRepository
from ingenious.models.message import Message


class MockSQLRepository(BaseSQLRepository):
    """Mock implementation of BaseSQLRepository for testing."""

    def __init__(self, config: Config.Config):
        self.connection_initialized = False
        self.executed_queries = []
        self.mock_results = {}
        super().__init__(config)

    def _init_connection(self) -> None:
        """Mock connection initialization."""
        self.connection_initialized = True

    def _execute_sql(
        self, sql: str, params: List[Any] = None, expect_results: bool = True
    ) -> Any:
        """Mock SQL execution with configurable results."""
        if params is None:
            params = []

        self.executed_queries.append(
            {"sql": sql, "params": params, "expect_results": expect_results}
        )

        # Return mock results based on query type
        query_key = (
            sql.strip().split()[0].upper()
        )  # Get first word (INSERT, SELECT, etc.)

        if expect_results and query_key == "SELECT":
            return self.mock_results.get(sql, [])
        return None

    def _get_db_specific_query(self, query_type: str, **kwargs) -> str:
        """Mock database-specific queries."""
        queries = {
            "create_chat_history_table": "CREATE TABLE chat_history (...);",
            "create_chat_history_summary_table": "CREATE TABLE chat_history_summary (...);",
            "create_users_table": "CREATE TABLE users (...);",
            "create_threads_table": "CREATE TABLE threads (...);",
            "create_steps_table": "CREATE TABLE steps (...);",
            "create_elements_table": "CREATE TABLE elements (...);",
            "create_feedbacks_table": "CREATE TABLE feedbacks (...);",
            "insert_message": "INSERT INTO chat_history (...) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            "insert_memory": "INSERT INTO chat_history_summary (...) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            "select_message": "SELECT * FROM chat_history WHERE message_id = ? AND thread_id = ?",
            "select_latest_memory": "SELECT * FROM chat_history_summary WHERE thread_id = ? ORDER BY timestamp DESC LIMIT 1",
            "update_message_feedback": "UPDATE chat_history SET positive_feedback = ? WHERE message_id = ? AND thread_id = ?",
            "update_memory_feedback": "UPDATE chat_history_summary SET positive_feedback = ? WHERE message_id = ? AND thread_id = ?",
            "update_message_content_filter": "UPDATE chat_history SET content_filter_results = ? WHERE message_id = ? AND thread_id = ?",
            "update_memory_content_filter": "UPDATE chat_history_summary SET content_filter_results = ? WHERE message_id = ? AND thread_id = ?",
            "insert_user": "INSERT INTO users (...) VALUES (?, ?, ?, ?)",
            "select_user": "SELECT * FROM users WHERE identifier = ?",
            "select_thread_messages": "SELECT * FROM chat_history WHERE thread_id = ? ORDER BY timestamp ASC LIMIT 5",
            "select_thread_memory": "SELECT * FROM chat_history_summary WHERE thread_id = ? ORDER BY timestamp DESC LIMIT 1",
            "delete_thread": "DELETE FROM chat_history WHERE thread_id = ?",
            "delete_thread_memory": "DELETE FROM chat_history_summary WHERE thread_id = ?",
            "delete_user_memory": "DELETE FROM chat_history_summary WHERE user_id = ?",
        }
        return queries.get(query_type, "")

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str]
    ) -> Optional[List[IChatHistoryRepository.ThreadDict]]:
        """Mock implementation for get_threads_for_user."""
        return []

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Mock implementation for update_thread."""
        return thread_id


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = MagicMock()
    config.chat_history = MagicMock()
    config.chat_history.database_path = "/tmp/test.db"
    config.chat_history.database_connection_string = "test_connection_string"
    return config


@pytest.fixture
def mock_repository(mock_config):
    """Create a mock repository instance for testing."""
    return MockSQLRepository(mock_config)


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    return Message(
        user_id="user123",
        thread_id="thread456",
        message_id="msg789",
        positive_feedback=None,
        timestamp=datetime.now(),
        role="user",
        content="Test message content",
        content_filter_results=None,
        tool_calls=None,
        tool_call_id=None,
        tool_call_function=None,
    )


class TestBaseSQLRepository:
    """Test cases for BaseSQLRepository abstract class."""

    def test_initialization(self, mock_repository):
        """Test that repository initializes correctly."""
        assert mock_repository.connection_initialized is True
        assert len(mock_repository.executed_queries) == 7  # 7 table creation queries

        # Verify all table creation queries were executed
        table_queries = [q["sql"] for q in mock_repository.executed_queries]
        assert all("CREATE TABLE" in query for query in table_queries)

    @pytest.mark.asyncio
    async def test_add_message(self, mock_repository, sample_message):
        """Test adding a message."""
        # Reset the executed queries to focus on this operation
        mock_repository.executed_queries = []

        result = await mock_repository.add_message(sample_message)

        # Verify message ID was generated and returned
        assert result is not None
        assert isinstance(result, str)

        # Verify SQL was executed
        assert len(mock_repository.executed_queries) == 1
        query = mock_repository.executed_queries[0]
        assert "INSERT INTO chat_history" in query["sql"]
        assert len(query["params"]) == 11
        assert query["expect_results"] is False

    @pytest.mark.asyncio
    async def test_add_memory(self, mock_repository, sample_message):
        """Test adding a memory message."""
        mock_repository.executed_queries = []

        result = await mock_repository.add_memory(sample_message)

        # Verify message ID was generated and returned
        assert result is not None
        assert isinstance(result, str)

        # Verify SQL was executed
        assert len(mock_repository.executed_queries) == 1
        query = mock_repository.executed_queries[0]
        assert "INSERT INTO chat_history_summary" in query["sql"]
        assert len(query["params"]) == 11
        assert query["expect_results"] is False

    @pytest.mark.asyncio
    async def test_get_message_found(self, mock_repository):
        """Test getting a message that exists."""
        # Mock the database result
        mock_repository.mock_results = {
            "SELECT * FROM chat_history WHERE message_id = ? AND thread_id = ?": [
                {
                    "user_id": "user123",
                    "thread_id": "thread456",
                    "message_id": "msg789",
                    "positive_feedback": None,
                    "timestamp": datetime.now(),
                    "role": "user",
                    "content": "Test content",
                    "content_filter_results": None,
                    "tool_calls": None,
                    "tool_call_id": None,
                    "tool_call_function": None,
                }
            ]
        }

        result = await mock_repository.get_message("msg789", "thread456")

        assert result is not None
        assert isinstance(result, Message)
        assert result.message_id == "msg789"
        assert result.thread_id == "thread456"
        assert result.user_id == "user123"
        assert result.content == "Test content"

    @pytest.mark.asyncio
    async def test_get_message_not_found(self, mock_repository):
        """Test getting a message that doesn't exist."""
        # Mock empty result
        mock_repository.mock_results = {
            "SELECT * FROM chat_history WHERE message_id = ? AND thread_id = ?": []
        }

        result = await mock_repository.get_message("nonexistent", "thread456")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_memory(self, mock_repository):
        """Test getting memory for a thread."""
        # Mock the database result
        mock_repository.mock_results = {
            "SELECT * FROM chat_history_summary WHERE thread_id = ? ORDER BY timestamp DESC LIMIT 1": [
                {
                    "user_id": "user123",
                    "thread_id": "thread456",
                    "message_id": "memory789",
                    "positive_feedback": True,
                    "timestamp": datetime.now(),
                    "role": "assistant",
                    "content": "Memory content",
                    "content_filter_results": None,
                    "tool_calls": None,
                    "tool_call_id": None,
                    "tool_call_function": None,
                }
            ]
        }

        result = await mock_repository.get_memory("msg789", "thread456")

        assert result is not None
        assert isinstance(result, Message)
        assert result.message_id == "memory789"
        assert result.content == "Memory content"
        assert result.positive_feedback is True

    @pytest.mark.asyncio
    async def test_update_message_feedback(self, mock_repository):
        """Test updating message feedback."""
        mock_repository.executed_queries = []

        await mock_repository.update_message_feedback("msg789", "thread456", True)

        assert len(mock_repository.executed_queries) == 1
        query = mock_repository.executed_queries[0]
        assert "UPDATE chat_history" in query["sql"]
        assert "positive_feedback" in query["sql"]
        assert query["params"] == [True, "msg789", "thread456"]
        assert query["expect_results"] is False

    @pytest.mark.asyncio
    async def test_update_memory_feedback(self, mock_repository):
        """Test updating memory feedback."""
        mock_repository.executed_queries = []

        await mock_repository.update_memory_feedback("msg789", "thread456", False)

        assert len(mock_repository.executed_queries) == 1
        query = mock_repository.executed_queries[0]
        assert "UPDATE chat_history_summary" in query["sql"]
        assert "positive_feedback" in query["sql"]
        assert query["params"] == [False, "msg789", "thread456"]
        assert query["expect_results"] is False

    @pytest.mark.asyncio
    async def test_update_message_content_filter_results(self, mock_repository):
        """Test updating message content filter results."""
        mock_repository.executed_queries = []

        filter_results = {"violence": 0.1, "hate": 0.05}
        await mock_repository.update_message_content_filter_results(
            "msg789", "thread456", filter_results
        )

        assert len(mock_repository.executed_queries) == 1
        query = mock_repository.executed_queries[0]
        assert "UPDATE chat_history" in query["sql"]
        assert "content_filter_results" in query["sql"]
        assert query["params"][0] == str(filter_results)
        assert query["expect_results"] is False

    @pytest.mark.asyncio
    async def test_add_user(self, mock_repository):
        """Test adding a new user."""
        mock_repository.executed_queries = []

        result = await mock_repository.add_user("test_user", {"role": "admin"})

        assert result is not None
        assert isinstance(result, IChatHistoryRepository.User)
        assert result.identifier == "test_user"
        assert result.metadata == {"role": "admin"}
        assert isinstance(result.id, uuid.UUID)

        # Verify SQL was executed
        assert len(mock_repository.executed_queries) == 1
        query = mock_repository.executed_queries[0]
        assert "INSERT INTO users" in query["sql"]
        assert len(query["params"]) == 4
        assert query["params"][1] == "test_user"
        assert query["params"][2] == json.dumps({"role": "admin"})

    @pytest.mark.asyncio
    async def test_get_user_existing(self, mock_repository):
        """Test getting an existing user."""
        # Mock the database result
        mock_repository.mock_results = {
            "SELECT * FROM users WHERE identifier = ?": [
                {
                    "id": str(uuid.uuid4()),
                    "identifier": "existing_user",
                    "metadata": '{"role": "user"}',
                    "createdAt": "2023-01-01T00:00:00.000000+00:00",
                }
            ]
        }

        result = await mock_repository.get_user("existing_user")

        assert result is not None
        assert isinstance(result, IChatHistoryRepository.User)
        assert result.identifier == "existing_user"

    @pytest.mark.asyncio
    async def test_get_user_new(self, mock_repository):
        """Test getting a user that doesn't exist (should create new)."""
        # Mock empty result for initial query, then return created user
        mock_repository.mock_results = {"SELECT * FROM users WHERE identifier = ?": []}

        result = await mock_repository.get_user("new_user")

        assert result is not None
        assert isinstance(result, IChatHistoryRepository.User)
        assert result.identifier == "new_user"

        # Verify user was created
        insert_queries = [
            q
            for q in mock_repository.executed_queries
            if "INSERT INTO users" in q["sql"]
        ]
        assert len(insert_queries) == 1

    @pytest.mark.asyncio
    async def test_get_thread_messages(self, mock_repository):
        """Test getting messages for a thread."""
        # Mock the database result
        mock_repository.mock_results = {
            "SELECT * FROM chat_history WHERE thread_id = ? ORDER BY timestamp ASC LIMIT 5": [
                {
                    "user_id": "user123",
                    "thread_id": "thread456",
                    "message_id": "msg1",
                    "positive_feedback": None,
                    "timestamp": datetime.now(),
                    "role": "user",
                    "content": "Message 1",
                    "content_filter_results": None,
                    "tool_calls": None,
                    "tool_call_id": None,
                    "tool_call_function": None,
                },
                {
                    "user_id": "user123",
                    "thread_id": "thread456",
                    "message_id": "msg2",
                    "positive_feedback": None,
                    "timestamp": datetime.now(),
                    "role": "assistant",
                    "content": "Message 2",
                    "content_filter_results": None,
                    "tool_calls": None,
                    "tool_call_id": None,
                    "tool_call_function": None,
                },
            ]
        }

        result = await mock_repository.get_thread_messages("thread456")

        assert len(result) == 2
        assert all(isinstance(msg, Message) for msg in result)
        assert result[0].message_id == "msg1"
        assert result[1].message_id == "msg2"

    @pytest.mark.asyncio
    async def test_delete_thread(self, mock_repository):
        """Test deleting a thread."""
        mock_repository.executed_queries = []

        await mock_repository.delete_thread("thread456")

        assert len(mock_repository.executed_queries) == 1
        query = mock_repository.executed_queries[0]
        assert "DELETE FROM chat_history" in query["sql"]
        assert query["params"] == ["thread456"]
        assert query["expect_results"] is False

    @pytest.mark.asyncio
    async def test_delete_thread_memory(self, mock_repository):
        """Test deleting thread memory."""
        mock_repository.executed_queries = []

        await mock_repository.delete_thread_memory("thread456")

        assert len(mock_repository.executed_queries) == 1
        query = mock_repository.executed_queries[0]
        assert "DELETE FROM chat_history_summary" in query["sql"]
        assert query["params"] == ["thread456"]
        assert query["expect_results"] is False

    @pytest.mark.asyncio
    async def test_delete_user_memory(self, mock_repository):
        """Test deleting user memory."""
        mock_repository.executed_queries = []

        await mock_repository.delete_user_memory("user123")

        assert len(mock_repository.executed_queries) == 1
        query = mock_repository.executed_queries[0]
        assert "DELETE FROM chat_history_summary" in query["sql"]
        assert query["params"] == ["user123"]
        assert query["expect_results"] is False

    def test_row_to_message_dict_format(self, mock_repository):
        """Test converting dictionary row to Message object."""
        row_dict = {
            "user_id": "user123",
            "thread_id": "thread456",
            "message_id": "msg789",
            "positive_feedback": True,
            "timestamp": datetime.now(),
            "role": "user",
            "content": "Test content",
            "content_filter_results": None,
            "tool_calls": None,
            "tool_call_id": None,
            "tool_call_function": None,
        }

        message = mock_repository._row_to_message(row_dict)

        assert isinstance(message, Message)
        assert message.user_id == "user123"
        assert message.thread_id == "thread456"
        assert message.message_id == "msg789"
        assert message.positive_feedback is True
        assert message.content == "Test content"

    def test_row_to_message_tuple_format(self, mock_repository):
        """Test converting tuple/list row to Message object."""
        row_tuple = (
            "user123",
            "thread456",
            "msg789",
            True,
            datetime.now(),
            "user",
            "Test content",
            None,
            None,
            None,
            None,
        )

        message = mock_repository._row_to_message(row_tuple)

        assert isinstance(message, Message)
        assert message.user_id == "user123"
        assert message.thread_id == "thread456"
        assert message.message_id == "msg789"
        assert message.positive_feedback is True
        assert message.content == "Test content"

    def test_row_to_user_dict_format(self, mock_repository):
        """Test converting dictionary row to User object."""
        row_dict = {
            "id": str(uuid.uuid4()),
            "identifier": "test_user",
            "metadata": '{"role": "admin"}',
            "createdAt": "2023-01-01T00:00:00.000000+00:00",
        }

        user = mock_repository._row_to_user(row_dict)

        assert isinstance(user, IChatHistoryRepository.User)
        assert user.identifier == "test_user"
        assert user.metadata == '{"role": "admin"}'
        assert user.createdAt == "2023-01-01T00:00:00.000000+00:00"

    def test_row_to_user_tuple_format(self, mock_repository):
        """Test converting tuple/list row to User object."""
        test_id = str(uuid.uuid4())
        row_tuple = (
            test_id,
            "test_user",
            '{"role": "admin"}',
            "2023-01-01T00:00:00.000000+00:00",
        )

        user = mock_repository._row_to_user(row_tuple)

        assert isinstance(user, IChatHistoryRepository.User)
        assert user.id == test_id
        assert user.identifier == "test_user"
        assert user.metadata == '{"role": "admin"}'
        assert user.createdAt == "2023-01-01T00:00:00.000000+00:00"

    def test_get_db_specific_query_coverage(self, mock_repository):
        """Test that all required queries are available."""
        required_queries = [
            "create_chat_history_table",
            "create_chat_history_summary_table",
            "create_users_table",
            "create_threads_table",
            "create_steps_table",
            "create_elements_table",
            "create_feedbacks_table",
            "insert_message",
            "insert_memory",
            "select_message",
            "select_latest_memory",
            "update_message_feedback",
            "update_memory_feedback",
            "update_message_content_filter",
            "update_memory_content_filter",
            "insert_user",
            "select_user",
            "select_thread_messages",
            "select_thread_memory",
            "delete_thread",
            "delete_thread_memory",
            "delete_user_memory",
        ]

        for query_type in required_queries:
            query = mock_repository._get_db_specific_query(query_type)
            assert query != "", f"Query '{query_type}' should not be empty"
            assert isinstance(query, str), f"Query '{query_type}' should be a string"
