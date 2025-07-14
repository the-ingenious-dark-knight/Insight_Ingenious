"""Tests for SQLite connection pool implementation."""

import asyncio
import os
import sqlite3
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock

import pytest

from ingenious.config.config import IngeniousSettings
from ingenious.db.sqlite import ConnectionPool, sqlite_ChatHistoryRepository
from ingenious.models.message import Message


class TestConnectionPool:
    """Test suite for ConnectionPool class."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        try:
            os.unlink(db_path)
        except OSError:
            pass

    @pytest.fixture
    def connection_pool(self, temp_db_path):
        """Create a connection pool for testing."""
        pool = ConnectionPool(temp_db_path, pool_size=5)
        yield pool
        pool.close_all()

    def test_pool_initialization(self, temp_db_path):
        """Test that the connection pool initializes correctly."""
        pool = ConnectionPool(temp_db_path, pool_size=3)

        # Check that pool is created with correct configuration
        assert pool.db_path == temp_db_path
        assert pool.pool_size == 3
        assert pool.max_retries == 3
        assert pool.retry_delay == 0.1
        assert pool._created_connections <= 3

        pool.close_all()

    def test_get_connection_basic(self, connection_pool):
        """Test basic connection retrieval from pool."""
        with connection_pool.get_connection() as conn:
            assert conn is not None
            assert isinstance(conn, sqlite3.Connection)

            # Test that connection works
            cursor = conn.cursor()
            result = cursor.execute("SELECT 1").fetchone()
            assert result[0] == 1

    def test_connection_health_check(self, connection_pool):
        """Test that connection health checks work correctly."""
        with connection_pool.get_connection() as conn:
            # Test healthy connection
            assert connection_pool._is_connection_healthy(conn)

            # Close connection and test unhealthy
            conn.close()
            assert not connection_pool._is_connection_healthy(conn)

    def test_concurrent_connections(self, connection_pool):
        """Test that multiple threads can get connections concurrently."""
        results = []
        errors = []

        def get_connection_and_query(thread_id):
            try:
                with connection_pool.get_connection() as conn:
                    cursor = conn.cursor()
                    result = cursor.execute("SELECT ?", (thread_id,)).fetchone()
                    results.append((thread_id, result[0]))
                    time.sleep(0.1)  # Simulate work
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=get_connection_and_query, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert set(r[0] for r in results) == set(range(10))

    def test_connection_reuse(self, connection_pool):
        """Test that connections are properly reused."""
        initial_count = connection_pool._created_connections

        # Use connections multiple times
        for _ in range(20):
            with connection_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")

        # Should not have created many new connections due to reuse
        assert (
            connection_pool._created_connections
            <= initial_count + connection_pool.pool_size
        )

    def test_pool_stress_test(self, temp_db_path):
        """Stress test the connection pool with many concurrent operations."""
        pool = ConnectionPool(temp_db_path, pool_size=5)

        def worker(worker_id):
            results = []
            for i in range(50):
                try:
                    with pool.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS test_table (
                                id INTEGER PRIMARY KEY,
                                worker_id INTEGER,
                                iteration INTEGER,
                                data TEXT
                            )
                        """)
                        cursor.execute(
                            """
                            INSERT INTO test_table (worker_id, iteration, data)
                            VALUES (?, ?, ?)
                        """,
                            (worker_id, i, f"data_{worker_id}_{i}"),
                        )
                        conn.commit()

                        # Read back data
                        cursor.execute(
                            """
                            SELECT COUNT(*) FROM test_table
                            WHERE worker_id = ?
                        """,
                            (worker_id,),
                        )
                        count = cursor.fetchone()[0]
                        results.append(count)
                except Exception as e:
                    results.append(f"ERROR: {e}")
            return worker_id, results

        # Run stress test with multiple workers
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]

            worker_results = {}
            for future in as_completed(futures):
                worker_id, results = future.result()
                worker_results[worker_id] = results

        # Verify all workers completed successfully
        for worker_id, results in worker_results.items():
            assert len(results) == 50, (
                f"Worker {worker_id} didn't complete all iterations"
            )
            # Check that no errors occurred
            error_count = sum(
                1 for r in results if isinstance(r, str) and r.startswith("ERROR:")
            )
            assert error_count == 0, (
                f"Worker {worker_id} had errors: {[r for r in results if isinstance(r, str)]}"
            )

        pool.close_all()

    def test_connection_failure_recovery(self, temp_db_path):
        """Test that the pool recovers from connection failures."""
        pool = ConnectionPool(temp_db_path, pool_size=1, max_retries=3)

        # Clear the pool to force new connection creation
        pool.close_all()

        # Simulate database file corruption/removal
        original_create = pool._create_connection
        call_count = 0

        def failing_create():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # Fail first two attempts
                raise sqlite3.Error("Simulated connection failure")
            return original_create()

        # Mock the _create_connection method
        pool._create_connection = failing_create

        try:
            # This should eventually succeed after retries
            with pool.get_connection() as conn:
                assert conn is not None
                cursor = conn.cursor()
                result = cursor.execute("SELECT 1").fetchone()
                assert result[0] == 1

            assert call_count >= 2  # Should have retried
        finally:
            # Restore original method
            pool._create_connection = original_create
            pool.close_all()

    def test_pool_close_all(self, connection_pool):
        """Test that close_all properly closes all connections."""
        # Get some connections to populate the pool
        with connection_pool.get_connection():
            pass

        initial_count = connection_pool._created_connections
        assert initial_count > 0

        # Close all connections
        connection_pool.close_all()

        # Check that counter is reset
        assert connection_pool._created_connections == 0


class TestSQLiteRepositoryWithPool:
    """Test suite for sqlite_ChatHistoryRepository using connection pool."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        try:
            os.unlink(db_path)
        except OSError:
            pass

    @pytest.fixture
    def config(self, temp_db_path):
        """Create a test configuration."""
        config = MagicMock(spec=IngeniousSettings)
        config.chat_history = MagicMock()
        config.chat_history.database_path = temp_db_path
        config.chat_history.connection_pool_size = 5
        return config

    @pytest.fixture
    def repository(self, config):
        """Create a repository instance for testing."""
        repo = sqlite_ChatHistoryRepository(config)
        yield repo
        repo.close()

    def test_repository_initialization(self, config):
        """Test that repository initializes with connection pool."""
        repo = sqlite_ChatHistoryRepository(config)

        # Check that pool is created
        assert hasattr(repo, "pool")
        assert isinstance(repo.pool, ConnectionPool)
        assert repo.pool.pool_size == 5

        repo.close()

    def test_repository_table_creation(self, repository):
        """Test that tables are created successfully using the pool."""
        # Tables should be created during initialization
        # Verify by checking if we can query them
        result = repository.execute_sql(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('chat_history', 'users', 'threads')
        """,
            expect_results=True,
        )

        table_names = [row["name"] for row in result]
        assert "chat_history" in table_names
        assert "users" in table_names
        assert "threads" in table_names

    @pytest.mark.asyncio
    async def test_repository_operations(self, repository):
        """Test basic repository operations using connection pool."""
        # Test adding a user
        user = await repository.add_user("test_user", {"role": "tester"})
        assert user.identifier == "test_user"

        # Test getting the user
        retrieved_user = await repository.get_user("test_user")
        assert retrieved_user.identifier == "test_user"

        # Test adding a message
        message = Message(
            user_id=str(user.id),
            thread_id="test_thread",
            role="user",
            content="Test message content",
        )
        message_id = await repository.add_message(message)
        assert message_id is not None

        # Test retrieving the message
        retrieved_message = await repository.get_message(message_id, "test_thread")
        assert retrieved_message.content == "Test message content"

    def test_repository_concurrent_operations(self, repository):
        """Test concurrent operations on the repository."""

        def worker(worker_id):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def async_work():
                # Add a user
                user = await repository.add_user(
                    f"user_{worker_id}", {"worker": worker_id}
                )

                # Add multiple messages
                messages = []
                for i in range(5):
                    message = Message(
                        user_id=str(user.id),
                        thread_id=f"thread_{worker_id}",
                        role="user" if i % 2 == 0 else "assistant",
                        content=f"Message {i} from worker {worker_id}",
                    )
                    message_id = await repository.add_message(message)
                    messages.append(message_id)

                return worker_id, len(messages)

            try:
                return loop.run_until_complete(async_work())
            finally:
                loop.close()

        # Run multiple workers concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(5)]

            results = []
            for future in as_completed(futures):
                worker_id, message_count = future.result()
                results.append((worker_id, message_count))

        # Verify all workers completed successfully
        assert len(results) == 5
        for worker_id, message_count in results:
            assert message_count == 5, (
                f"Worker {worker_id} didn't complete all operations"
            )

    def test_repository_cleanup(self, config):
        """Test that repository properly cleans up connections."""
        repo = sqlite_ChatHistoryRepository(config)
        # Use the repository
        repo.execute_sql("SELECT 1", expect_results=True)

        # Close the repository
        repo.close()

        # Verify connections are cleaned up
        assert repo.pool._created_connections == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
