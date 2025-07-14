import asyncio
import os
import sqlite3
import tempfile
import uuid
from datetime import datetime
from unittest.mock import Mock

import pytest

from ingenious.db.connection_pool import ConnectionPool, SQLiteConnectionFactory
from ingenious.db.query_builder import AzureSQLDialect, QueryBuilder, SQLiteDialect
from ingenious.db.repository_factory import SQLiteChatHistoryRepository
from ingenious.models.message import Message


class TestSQLiteIntegration:
    """Integration tests for SQLite repository with real database."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary SQLite database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        # Cleanup
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def sqlite_repository(self, temp_db_path):
        """Create a SQLite repository with real components."""
        mock_config = Mock()
        mock_config.chat_history.database_path = temp_db_path

        # Create real components
        connection_factory = SQLiteConnectionFactory(temp_db_path)
        connection_pool = ConnectionPool(connection_factory, pool_size=2)
        query_builder = QueryBuilder(SQLiteDialect())

        return SQLiteChatHistoryRepository(mock_config, query_builder, connection_pool)

    def test_table_creation(self, sqlite_repository, temp_db_path):
        """Test that tables are created correctly."""
        # Tables should be created during repository initialization

        # Verify tables exist by querying SQLite metadata
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = [
            "chat_history",
            "chat_history_summary",
            "users",
            "threads",
            "steps",
            "elements",
            "feedbacks",
        ]

        for table in expected_tables:
            assert table in tables, f"Table {table} was not created"

        conn.close()

    def test_table_schema(self, sqlite_repository, temp_db_path):
        """Test that table schemas are correct."""
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Check chat_history table schema
        cursor.execute("PRAGMA table_info(chat_history)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type

        expected_columns = {
            "user_id": "TEXT",
            "thread_id": "TEXT",
            "message_id": "TEXT",
            "positive_feedback": "BOOLEAN",
            "timestamp": "TEXT",
            "role": "TEXT",
            "content": "TEXT",
            "content_filter_results": "TEXT",
            "tool_calls": "TEXT",
            "tool_call_id": "TEXT",
            "tool_call_function": "TEXT",
        }

        for col_name, col_type in expected_columns.items():
            assert col_name in columns, f"Column {col_name} not found"
            assert columns[col_name] == col_type, (
                f"Column {col_name} has wrong type: {columns[col_name]} != {col_type}"
            )

        conn.close()

    @pytest.mark.asyncio
    async def test_add_and_get_message(self, sqlite_repository):
        """Test adding and retrieving a message."""
        # Create test message
        message = Message(
            user_id="test_user_123",
            thread_id="test_thread_456",
            role="user",
            content="Hello, world!",
            positive_feedback=None,
            content_filter_results=None,
            tool_calls=None,
            tool_call_id=None,
            tool_call_function=None,
        )

        # Add message
        message_id = await sqlite_repository.add_message(message)
        assert message_id is not None
        assert isinstance(message_id, str)

        # Retrieve message
        retrieved_message = await sqlite_repository.get_message(
            message_id, message.thread_id
        )

        assert retrieved_message is not None
        assert retrieved_message.user_id == message.user_id
        assert retrieved_message.thread_id == message.thread_id
        assert retrieved_message.role == message.role
        assert retrieved_message.content == message.content
        assert retrieved_message.message_id == message_id

    @pytest.mark.asyncio
    async def test_add_and_get_user(self, sqlite_repository):
        """Test adding and retrieving a user."""
        identifier = "test_user@example.com"
        metadata = {"name": "Test User", "role": "tester"}

        # Add user
        user = await sqlite_repository.add_user(identifier, metadata)

        assert user is not None
        assert user.identifier == identifier
        assert user.metadata == metadata
        assert user.id is not None

        # Retrieve user
        retrieved_user = await sqlite_repository.get_user(identifier)

        assert retrieved_user is not None
        assert retrieved_user.identifier == identifier
        assert str(retrieved_user.id) == str(user.id)

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_creates_user(self, sqlite_repository):
        """Test that getting a nonexistent user creates the user."""
        identifier = "new_user@example.com"

        # User should not exist yet
        user = await sqlite_repository.get_user(identifier)

        # Should create and return the user
        assert user is not None
        assert user.identifier == identifier

        # Should be able to retrieve it again
        user2 = await sqlite_repository.get_user(identifier)
        assert str(user2.id) == str(user.id)

    @pytest.mark.asyncio
    async def test_update_message_feedback(self, sqlite_repository):
        """Test updating message feedback."""
        # Create and add message
        message = Message(
            user_id="test_user_123",
            thread_id="test_thread_456",
            role="assistant",
            content="How can I help you?",
            positive_feedback=None,
        )

        message_id = await sqlite_repository.add_message(message)

        # Update feedback
        await sqlite_repository.update_message_feedback(
            message_id, message.thread_id, True
        )

        # Retrieve and verify
        retrieved_message = await sqlite_repository.get_message(
            message_id, message.thread_id
        )
        assert retrieved_message.positive_feedback is True

        # Update again
        await sqlite_repository.update_message_feedback(
            message_id, message.thread_id, False
        )

        retrieved_message = await sqlite_repository.get_message(
            message_id, message.thread_id
        )
        assert retrieved_message.positive_feedback is False

    @pytest.mark.asyncio
    async def test_get_thread_messages(self, sqlite_repository):
        """Test retrieving messages for a thread."""
        thread_id = "test_thread_789"

        # Add multiple messages to the thread
        messages = []
        for i in range(3):
            message = Message(
                user_id="test_user_123",
                thread_id=thread_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i + 1}",
            )
            message_id = await sqlite_repository.add_message(message)
            message.message_id = message_id
            messages.append(message)

        # Retrieve thread messages
        thread_messages = await sqlite_repository.get_thread_messages(thread_id)

        assert len(thread_messages) == 3

        # Messages should be ordered by timestamp (oldest first due to ORDER BY timestamp ASC)
        for i, msg in enumerate(thread_messages):
            assert msg.content == f"Message {i + 1}"
            assert msg.thread_id == thread_id

    @pytest.mark.asyncio
    async def test_delete_thread(self, sqlite_repository):
        """Test deleting all messages in a thread."""
        thread_id = "test_thread_delete"

        # Add messages to thread
        for i in range(2):
            message = Message(
                user_id="test_user_123",
                thread_id=thread_id,
                role="user",
                content=f"Message to delete {i + 1}",
            )
            await sqlite_repository.add_message(message)

        # Verify messages exist
        thread_messages = await sqlite_repository.get_thread_messages(thread_id)
        assert len(thread_messages) == 2

        # Delete thread
        await sqlite_repository.delete_thread(thread_id)

        # Verify messages are gone
        thread_messages = await sqlite_repository.get_thread_messages(thread_id)
        assert len(thread_messages) == 0

    @pytest.mark.asyncio
    async def test_memory_operations(self, sqlite_repository):
        """Test memory (summary) operations."""
        thread_id = "test_thread_memory"

        # Add memory
        memory_message = Message(
            user_id="test_user_123",
            thread_id=thread_id,
            role="system",
            content="This is a memory summary",
        )

        memory_id = await sqlite_repository.add_memory(memory_message)
        assert memory_id is not None

        # Retrieve memory
        retrieved_memory = await sqlite_repository.get_memory("", thread_id)
        assert retrieved_memory is not None
        assert retrieved_memory.content == "This is a memory summary"
        assert retrieved_memory.role == "system"

        # Update memory feedback
        await sqlite_repository.update_memory_feedback(memory_id, thread_id, True)

        # Get thread memory
        thread_memory = await sqlite_repository.get_thread_memory(thread_id)
        assert len(thread_memory) == 1
        assert thread_memory[0].positive_feedback is True

    def test_connection_pool_functionality(self, temp_db_path):
        """Test that connection pool works correctly."""
        connection_factory = SQLiteConnectionFactory(temp_db_path)
        pool = ConnectionPool(connection_factory, pool_size=2)

        # Test getting multiple connections
        connections = []
        try:
            for _ in range(3):  # More than pool size
                conn_context = pool.get_connection()
                conn = conn_context.__enter__()
                connections.append((conn_context, conn))

                # Test that connection works
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1

        finally:
            # Clean up connections
            for conn_context, conn in connections:
                try:
                    conn_context.__exit__(None, None, None)
                except Exception:
                    pass

            pool.close_all()

    def test_query_builder_generates_working_sql(self, temp_db_path):
        """Test that QueryBuilder generates SQL that actually works."""
        builder = QueryBuilder(SQLiteDialect())

        # Test table creation
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Create tables using query builder
        table_queries = [
            builder.create_chat_history_table(),
            builder.create_users_table(),
        ]

        for query in table_queries:
            cursor.execute(query)

        # Test insert using query builder
        insert_query = builder.insert_user()
        user_id = str(uuid.uuid4())
        cursor.execute(
            insert_query,
            [user_id, "test@example.com", "{}", datetime.now().isoformat()],
        )

        # Test select using query builder
        select_query = builder.select_user()
        cursor.execute(select_query, ["test@example.com"])
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == user_id
        assert result[1] == "test@example.com"

        conn.close()


class TestDatabaseAgnosticBehavior:
    """Test that the repository pattern works consistently across different scenarios."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary SQLite database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_dialect_compatibility(self, temp_db_path):
        """Test that both dialects produce compatible query structures."""
        sqlite_builder = QueryBuilder(SQLiteDialect())
        azuresql_builder = QueryBuilder(AzureSQLDialect())

        # Test that core queries have same parameter structure
        sqlite_insert = sqlite_builder.insert_message()
        azuresql_insert = azuresql_builder.insert_message()

        # Both should use same number of parameters
        assert sqlite_insert.count("?") == azuresql_insert.count("?")

        # Test with actual SQLite database
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Create table with SQLite dialect
        cursor.execute(sqlite_builder.create_chat_history_table())

        # Insert data using SQLite dialect query
        test_data = [
            "user_123",
            "thread_456",
            "msg_789",
            True,
            datetime.now().isoformat(),
            "user",
            "Hello",
            None,
            None,
            None,
            None,
        ]

        cursor.execute(sqlite_insert, test_data)

        # Select using SQLite dialect
        select_query = sqlite_builder.select_message()
        cursor.execute(select_query, ["msg_789", "thread_456"])
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == "user_123"  # user_id
        assert result[6] == "Hello"  # content

        conn.close()

    @pytest.mark.asyncio
    async def test_repository_interface_consistency(self, temp_db_path):
        """Test that repository interface is consistent regardless of implementation."""
        mock_config = Mock()
        mock_config.chat_history.database_path = temp_db_path

        # Create repository
        connection_factory = SQLiteConnectionFactory(temp_db_path)
        connection_pool = ConnectionPool(connection_factory, pool_size=1)
        query_builder = QueryBuilder(SQLiteDialect())

        repo = SQLiteChatHistoryRepository(mock_config, query_builder, connection_pool)

        # Test that all expected methods exist and work
        test_message = Message(
            user_id="test_user",
            thread_id="test_thread",
            role="user",
            content="Test message",
        )

        # Test basic operations
        message_id = await repo.add_message(test_message)
        assert message_id is not None

        retrieved = await repo.get_message(message_id, test_message.thread_id)
        assert retrieved is not None
        assert retrieved.content == "Test message"

        await repo.update_message_feedback(message_id, test_message.thread_id, True)

        updated = await repo.get_message(message_id, test_message.thread_id)
        assert updated.positive_feedback is True

        thread_messages = await repo.get_thread_messages(test_message.thread_id)
        assert len(thread_messages) == 1

        # Test user operations
        user = await repo.add_user("test@example.com", {"name": "Test"})
        assert user.identifier == "test@example.com"

        retrieved_user = await repo.get_user("test@example.com")
        assert str(retrieved_user.id) == str(user.id)

        # Test cleanup
        await repo.delete_thread(test_message.thread_id)
        thread_messages = await repo.get_thread_messages(test_message.thread_id)
        assert len(thread_messages) == 0

        repo.close()


class TestPerformanceAndConcurrency:
    """Test performance characteristics and concurrent access."""

    @pytest.fixture
    def temp_db_path(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, temp_db_path):
        """Test that repository handles concurrent operations correctly."""
        mock_config = Mock()
        mock_config.chat_history.database_path = temp_db_path

        connection_factory = SQLiteConnectionFactory(temp_db_path)
        connection_pool = ConnectionPool(connection_factory, pool_size=3)
        query_builder = QueryBuilder(SQLiteDialect())

        repo = SQLiteChatHistoryRepository(mock_config, query_builder, connection_pool)

        async def add_messages(thread_suffix, count=5):
            """Add multiple messages concurrently."""
            thread_id = f"concurrent_thread_{thread_suffix}"
            message_ids = []

            for i in range(count):
                message = Message(
                    user_id=f"user_{thread_suffix}",
                    thread_id=thread_id,
                    role="user",
                    content=f"Concurrent message {i} from thread {thread_suffix}",
                )
                message_id = await repo.add_message(message)
                message_ids.append(message_id)

            return thread_id, message_ids

        # Run concurrent operations
        tasks = [add_messages(i) for i in range(3)]
        results = await asyncio.gather(*tasks)

        # Verify all operations completed successfully
        assert len(results) == 3

        for thread_id, message_ids in results:
            assert len(message_ids) == 5

            # Verify messages were stored correctly
            thread_messages = await repo.get_thread_messages(thread_id)
            assert len(thread_messages) == 5

        repo.close()

    def test_connection_pool_stress(self, temp_db_path):
        """Test connection pool under stress."""
        connection_factory = SQLiteConnectionFactory(temp_db_path)
        pool = ConnectionPool(connection_factory, pool_size=2, max_retries=5)

        # Create tables first
        with pool.get_connection() as conn:
            conn.execute("""
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    value TEXT
                )
            """)

        # Simulate high concurrent usage
        def use_connection(iteration):
            try:
                with pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO test_table (value) VALUES (?)",
                        [f"value_{iteration}"],
                    )
                    cursor.execute("SELECT COUNT(*) FROM test_table")
                    count = cursor.fetchone()[0]
                    return count
            except Exception as e:
                return f"Error: {e}"

        # Test multiple concurrent connections
        import threading

        results = []
        threads = []

        for i in range(10):  # More threads than pool size
            thread = threading.Thread(
                target=lambda i=i: results.append(use_connection(i))
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All operations should complete successfully
        assert len(results) == 10
        error_count = sum(
            1 for r in results if isinstance(r, str) and r.startswith("Error")
        )
        assert error_count == 0, (
            f"Got {error_count} errors: {[r for r in results if isinstance(r, str)]}"
        )

        pool.close_all()
