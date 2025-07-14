from unittest.mock import Mock, patch

import pytest

from ingenious.db.connection_pool import (
    AzureSQLConnectionFactory,
    ConnectionPool,
    SQLiteConnectionFactory,
)
from ingenious.db.query_builder import AzureSQLDialect, QueryBuilder, SQLiteDialect
from ingenious.db.repository_factory import (
    AzureSQLChatHistoryRepository,
    ModernRepositoryFactory,
    RepositoryFactory,
    SQLiteChatHistoryRepository,
)
from ingenious.models.database_client import DatabaseClientType


class TestConnectionPool:
    """Test the database-agnostic connection pool."""

    def test_sqlite_connection_factory(self):
        factory = SQLiteConnectionFactory(":memory:")

        # Test connection creation
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn

            conn = factory.create_connection()
            assert conn == mock_conn

            # Verify SQLite-specific settings were applied
            mock_conn.execute.assert_any_call("PRAGMA journal_mode=WAL")
            mock_conn.execute.assert_any_call("PRAGMA synchronous=NORMAL")

    def test_azuresql_connection_factory(self):
        factory = AzureSQLConnectionFactory("test_connection_string")

        with patch("pyodbc.connect") as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn

            conn = factory.create_connection()
            assert conn == mock_conn

            # Verify Azure SQL-specific settings
            assert mock_conn.autocommit is True

    def test_connection_pool_initialization(self):
        mock_factory = Mock()
        mock_conn = Mock()
        mock_factory.create_connection.return_value = mock_conn
        mock_factory.is_connection_healthy.return_value = True

        ConnectionPool(mock_factory, pool_size=2)

        # Should create initial connections
        assert mock_factory.create_connection.call_count == 2
        assert mock_factory.is_connection_healthy.call_count == 2

    def test_connection_pool_get_connection(self):
        mock_factory = Mock()
        mock_conn = Mock()
        mock_factory.create_connection.return_value = mock_conn
        mock_factory.is_connection_healthy.return_value = True

        pool = ConnectionPool(mock_factory, pool_size=1)

        with pool.get_connection() as conn:
            assert conn == mock_conn


class TestRepositoryFactory:
    """Test repository factory functionality."""

    def test_repository_factory_sqlite(self):
        mock_config = Mock()
        mock_config.chat_history.database_path = "/test/path/db.sqlite"

        with patch(
            "ingenious.db.sqlite.sqlite_ChatHistoryRepository"
        ) as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo

            repo = RepositoryFactory.create_chat_history_repository(
                DatabaseClientType.SQLITE, mock_config
            )

            assert repo == mock_repo
            mock_repo_class.assert_called_once_with(mock_config)

    def test_repository_factory_azuresql(self):
        mock_config = Mock()
        mock_config.chat_history.database_connection_string = "test_connection_string"

        with patch(
            "ingenious.db.azuresql.azuresql_ChatHistoryRepository"
        ) as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo

            repo = RepositoryFactory.create_chat_history_repository(
                DatabaseClientType.AZURESQL, mock_config
            )

            assert repo == mock_repo
            mock_repo_class.assert_called_once_with(mock_config)

    def test_repository_factory_unsupported_type(self):
        mock_config = Mock()

        with pytest.raises(ValueError, match="Unsupported database type"):
            RepositoryFactory.create_chat_history_repository("INVALID", mock_config)


class TestModernRepositoryFactory:
    """Test modern repository factory with composition."""

    @pytest.mark.skip(
        "Complex mocking needed - functionality tested in integration tests"
    )
    def test_modern_factory_sqlite(self):
        """Test would require complex mocking - functionality verified in integration tests."""
        pass

    @pytest.mark.skip(
        "Complex mocking needed - functionality tested in integration tests"
    )
    def test_modern_factory_azuresql(self):
        """Test would require complex mocking - functionality verified in integration tests."""
        pass

    def test_modern_factory_azuresql_missing_connection_string(self):
        mock_config = Mock()
        mock_config.chat_history.database_connection_string = None

        with pytest.raises(ValueError, match="Azure SQL connection string is required"):
            ModernRepositoryFactory.create_chat_history_repository(
                DatabaseClientType.AZURESQL, mock_config
            )


class TestSQLiteChatHistoryRepository:
    """Test SQLite repository with composition."""

    def test_initialization(self):
        mock_config = Mock()
        mock_builder = Mock()
        mock_pool = Mock()

        with patch.object(SQLiteChatHistoryRepository, "_create_tables"):
            repo = SQLiteChatHistoryRepository(mock_config, mock_builder, mock_pool)

            assert repo.config == mock_config
            assert repo.query_builder == mock_builder
            assert repo.pool == mock_pool

    def test_execute_sql_with_results(self):
        mock_config = Mock()
        mock_builder = Mock()
        mock_pool = Mock()

        # Mock connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_row = Mock()
        mock_row.__iter__ = Mock(return_value=iter([("value1", "value2")]))
        mock_cursor.execute.return_value.fetchall.return_value = [mock_row]
        mock_conn.cursor.return_value = mock_cursor
        mock_pool.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_pool.get_connection.return_value.__exit__ = Mock(return_value=False)

        with patch.object(SQLiteChatHistoryRepository, "_create_tables"):
            repo = SQLiteChatHistoryRepository(mock_config, mock_builder, mock_pool)

            # Mock the dict conversion behavior
            with patch(
                "builtins.dict", return_value={"col1": "value1", "col2": "value2"}
            ):
                result = repo._execute_sql("SELECT * FROM test", expect_results=True)

                mock_cursor.execute.assert_called_once_with("SELECT * FROM test", [])
                assert isinstance(result, list)

    def test_execute_sql_without_results(self):
        mock_config = Mock()
        mock_builder = Mock()
        mock_pool = Mock()

        mock_conn = Mock()
        mock_pool.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_pool.get_connection.return_value.__exit__ = Mock(return_value=False)

        with patch.object(SQLiteChatHistoryRepository, "_create_tables"):
            repo = SQLiteChatHistoryRepository(mock_config, mock_builder, mock_pool)

            repo._execute_sql(
                "INSERT INTO test VALUES (?)", ["value"], expect_results=False
            )

            mock_conn.execute.assert_called_once_with(
                "INSERT INTO test VALUES (?)", ["value"]
            )
            mock_conn.commit.assert_called_once()

    def test_close(self):
        mock_config = Mock()
        mock_builder = Mock()
        mock_pool = Mock()

        with patch.object(SQLiteChatHistoryRepository, "_create_tables"):
            repo = SQLiteChatHistoryRepository(mock_config, mock_builder, mock_pool)

            repo.close()
            mock_pool.close_all.assert_called_once()


class TestAzureSQLChatHistoryRepository:
    """Test Azure SQL repository with composition."""

    def test_initialization(self):
        mock_config = Mock()
        mock_builder = Mock()
        mock_pool = Mock()

        with patch.object(AzureSQLChatHistoryRepository, "_create_tables"):
            repo = AzureSQLChatHistoryRepository(mock_config, mock_builder, mock_pool)

            assert repo.config == mock_config
            assert repo.query_builder == mock_builder
            assert repo.pool == mock_pool

    def test_execute_sql_with_results(self):
        mock_config = Mock()
        mock_builder = Mock()
        mock_pool = Mock()

        # Mock connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("col1",), ("col2",)]
        mock_cursor.fetchall.return_value = [("value1", "value2")]
        mock_conn.cursor.return_value = mock_cursor
        mock_pool.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_pool.get_connection.return_value.__exit__ = Mock(return_value=False)

        with patch.object(AzureSQLChatHistoryRepository, "_create_tables"):
            repo = AzureSQLChatHistoryRepository(mock_config, mock_builder, mock_pool)

            result = repo._execute_sql("SELECT * FROM test", expect_results=True)

            mock_cursor.execute.assert_called_once_with("SELECT * FROM test", [])
            mock_cursor.close.assert_called_once()
            assert result == [{"col1": "value1", "col2": "value2"}]

    def test_execute_sql_without_results(self):
        mock_config = Mock()
        mock_builder = Mock()
        mock_pool = Mock()

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_pool.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_pool.get_connection.return_value.__exit__ = Mock(return_value=False)

        with patch.object(AzureSQLChatHistoryRepository, "_create_tables"):
            repo = AzureSQLChatHistoryRepository(mock_config, mock_builder, mock_pool)

            repo._execute_sql(
                "INSERT INTO test VALUES (?)", ["value"], expect_results=False
            )

            mock_cursor.execute.assert_called_once_with(
                "INSERT INTO test VALUES (?)", ["value"]
            )
            mock_conn.commit.assert_called_once()
            mock_cursor.close.assert_called_once()


class TestRepositoryIntegration:
    """Test integration between components."""

    def test_sqlite_repository_uses_query_builder(self):
        mock_config = Mock()
        mock_pool = Mock()
        mock_conn = Mock()
        mock_pool.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_pool.get_connection.return_value.__exit__ = Mock(return_value=False)

        builder = QueryBuilder(SQLiteDialect())

        with patch.object(SQLiteChatHistoryRepository, "_create_tables"):
            repo = SQLiteChatHistoryRepository(mock_config, builder, mock_pool)

            # Test that repository uses query builder for SQL generation
            query = repo.query_builder.insert_message()
            assert "INSERT INTO chat_history" in query
            assert query.count("?") == 11  # Should have 11 parameters

    def test_azuresql_repository_uses_query_builder(self):
        mock_config = Mock()
        mock_pool = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = []
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_pool.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_pool.get_connection.return_value.__exit__ = Mock(return_value=False)

        builder = QueryBuilder(AzureSQLDialect())

        with patch.object(AzureSQLChatHistoryRepository, "_create_tables"):
            repo = AzureSQLChatHistoryRepository(mock_config, builder, mock_pool)

            # Test that repository uses query builder for SQL generation
            query = repo.query_builder.select_latest_memory()
            assert "SELECT TOP 1" in query  # Azure SQL specific syntax

    def test_different_dialects_same_interface(self):
        """Test that repositories with different dialects have the same interface."""
        mock_config = Mock()
        mock_pool = Mock()

        sqlite_builder = QueryBuilder(SQLiteDialect())
        azuresql_builder = QueryBuilder(AzureSQLDialect())

        with (
            patch.object(SQLiteChatHistoryRepository, "_create_tables"),
            patch.object(AzureSQLChatHistoryRepository, "_create_tables"),
        ):
            sqlite_repo = SQLiteChatHistoryRepository(
                mock_config, sqlite_builder, mock_pool
            )
            azuresql_repo = AzureSQLChatHistoryRepository(
                mock_config, azuresql_builder, mock_pool
            )

            # Both should have the same interface methods
            assert hasattr(sqlite_repo, "_execute_sql")
            assert hasattr(azuresql_repo, "_execute_sql")

            assert hasattr(sqlite_repo, "query_builder")
            assert hasattr(azuresql_repo, "query_builder")

            # Both should be able to generate queries
            sqlite_query = sqlite_repo.query_builder.insert_message()
            azuresql_query = azuresql_repo.query_builder.insert_message()

            # Different syntax but same parameter count
            assert sqlite_query.count("?") == azuresql_query.count("?")


class TestErrorHandling:
    """Test error handling in repository pattern."""

    def test_sqlite_repository_database_error(self):
        mock_config = Mock()
        mock_builder = Mock()
        mock_pool = Mock()

        # Simulate database error
        mock_pool.get_connection.side_effect = Exception("Database connection failed")

        with patch.object(SQLiteChatHistoryRepository, "_create_tables"):
            repo = SQLiteChatHistoryRepository(mock_config, mock_builder, mock_pool)

            with pytest.raises(Exception):
                repo._execute_sql("SELECT * FROM test")

    def test_azuresql_repository_database_error(self):
        mock_config = Mock()
        mock_builder = Mock()
        mock_pool = Mock()

        # Simulate database error
        mock_pool.get_connection.side_effect = Exception("Database connection failed")

        with patch.object(AzureSQLChatHistoryRepository, "_create_tables"):
            repo = AzureSQLChatHistoryRepository(mock_config, mock_builder, mock_pool)

            with pytest.raises(Exception):
                repo._execute_sql("SELECT * FROM test")
