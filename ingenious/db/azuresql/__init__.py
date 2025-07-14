import json
from typing import Any, Dict, List, Optional

import pyodbc

import ingenious.config.config as Config
from ingenious.db.base_sql import BaseSQLRepository
from ingenious.db.chat_history_repository import IChatHistoryRepository


class azuresql_ChatHistoryRepository(BaseSQLRepository):
    def __init__(self, config: Config.Config):
        self.connection_string = config.chat_history.database_connection_string
        if not self.connection_string:
            raise ValueError(
                "Azure SQL connection string is required for azuresql chat history repository"
            )

        # Call parent constructor which will call _init_connection and _create_tables
        super().__init__(config)

    def _init_connection(self) -> None:
        """Initialize Azure SQL connection."""
        self.connection = pyodbc.connect(self.connection_string)
        self.connection.autocommit = True

    def _execute_sql(
        self, sql: str, params: List[Any] = None, expect_results: bool = True
    ) -> Any:
        """Execute SQL with Azure SQL connection handling."""
        if params is None:
            params = []
        cursor = None
        try:
            cursor = self.connection.cursor()

            if expect_results:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                # Convert to list of dictionaries
                columns = [column[0] for column in cursor.description]
                result = [dict(zip(columns, row)) for row in rows]
                return result
            else:
                cursor.execute(sql, params)
                self.connection.commit()

        except Exception as e:
            print(f"SQL Error: {e}")
            raise e

        finally:
            if cursor:
                cursor.close()

    def _get_db_specific_query(self, query_type: str, **kwargs) -> str:
        """Get Azure SQL-specific queries."""
        queries = {
            "create_chat_history_table": """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='chat_history' AND xtype='U')
                CREATE TABLE chat_history (
                    user_id NVARCHAR(255),
                    thread_id NVARCHAR(255),
                    message_id NVARCHAR(255),
                    positive_feedback BIT,
                    timestamp DATETIME2,
                    role NVARCHAR(50),
                    content NVARCHAR(MAX),
                    content_filter_results NVARCHAR(MAX),
                    tool_calls NVARCHAR(MAX),
                    tool_call_id NVARCHAR(255),
                    tool_call_function NVARCHAR(255)
                );
            """,
            "create_chat_history_summary_table": """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='chat_history_summary' AND xtype='U')
                CREATE TABLE chat_history_summary (
                    user_id NVARCHAR(255),
                    thread_id NVARCHAR(255),
                    message_id NVARCHAR(255),
                    positive_feedback BIT,
                    timestamp DATETIME2,
                    role NVARCHAR(50),
                    content NVARCHAR(MAX),
                    content_filter_results NVARCHAR(MAX),
                    tool_calls NVARCHAR(MAX),
                    tool_call_id NVARCHAR(255),
                    tool_call_function NVARCHAR(255)
                );
            """,
            "create_users_table": """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
                CREATE TABLE users (
                    id UNIQUEIDENTIFIER PRIMARY KEY,
                    identifier NVARCHAR(255) NOT NULL UNIQUE,
                    metadata NVARCHAR(MAX) NOT NULL,
                    createdAt DATETIME2
                );
            """,
            "create_threads_table": """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='threads' AND xtype='U')
                CREATE TABLE threads (
                    id UNIQUEIDENTIFIER PRIMARY KEY,
                    createdAt DATETIME2,
                    name NVARCHAR(255),
                    userId UNIQUEIDENTIFIER,
                    userIdentifier NVARCHAR(255),
                    tags NVARCHAR(MAX),
                    metadata NVARCHAR(MAX),
                    FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
                );
            """,
            "create_steps_table": """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='steps' AND xtype='U')
                CREATE TABLE steps (
                    id UNIQUEIDENTIFIER PRIMARY KEY,
                    name NVARCHAR(255) NOT NULL,
                    type NVARCHAR(50) NOT NULL,
                    threadId UNIQUEIDENTIFIER NOT NULL,
                    parentId UNIQUEIDENTIFIER,
                    disableFeedback BIT NOT NULL,
                    streaming BIT NOT NULL,
                    waitForAnswer BIT,
                    isError BIT,
                    metadata NVARCHAR(MAX),
                    tags NVARCHAR(MAX),
                    input NVARCHAR(MAX),
                    output NVARCHAR(MAX),
                    createdAt DATETIME2,
                    start DATETIME2,
                    [end] DATETIME2,
                    generation NVARCHAR(MAX),
                    showInput NVARCHAR(255),
                    language NVARCHAR(50),
                    indent INT
                );
            """,
            "create_elements_table": """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='elements' AND xtype='U')
                CREATE TABLE elements (
                    id UNIQUEIDENTIFIER PRIMARY KEY,
                    threadId UNIQUEIDENTIFIER,
                    type NVARCHAR(50),
                    url NVARCHAR(MAX),
                    chainlitKey NVARCHAR(255),
                    name NVARCHAR(255) NOT NULL,
                    display NVARCHAR(50),
                    objectKey NVARCHAR(255),
                    size NVARCHAR(50),
                    page INT,
                    language NVARCHAR(50),
                    forId UNIQUEIDENTIFIER,
                    mime NVARCHAR(100)
                );
            """,
            "create_feedbacks_table": """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='feedbacks' AND xtype='U')
                CREATE TABLE feedbacks (
                    id UNIQUEIDENTIFIER PRIMARY KEY,
                    forId UNIQUEIDENTIFIER NOT NULL,
                    threadId UNIQUEIDENTIFIER NOT NULL,
                    value INT NOT NULL,
                    comment NVARCHAR(MAX)
                );
            """,
            "insert_message": """
                INSERT INTO chat_history (
                    user_id, thread_id, message_id, positive_feedback, timestamp,
                    role, content, content_filter_results, tool_calls,
                    tool_call_id, tool_call_function)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            "insert_memory": """
                INSERT INTO chat_history_summary (
                    user_id, thread_id, message_id, positive_feedback, timestamp,
                    role, content, content_filter_results, tool_calls,
                    tool_call_id, tool_call_function)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            "select_message": """
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function
                FROM chat_history
                WHERE message_id = ? AND thread_id = ?
            """,
            "select_latest_memory": """
                SELECT TOP 1 user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function
                FROM chat_history_summary
                WHERE thread_id = ?
                ORDER BY timestamp DESC
            """,
            "update_message_feedback": """
                UPDATE chat_history
                SET positive_feedback = ?
                WHERE message_id = ? AND thread_id = ?
            """,
            "update_memory_feedback": """
                UPDATE chat_history_summary
                SET positive_feedback = ?
                WHERE message_id = ? AND thread_id = ?
            """,
            "update_message_content_filter": """
                UPDATE chat_history
                SET content_filter_results = ?
                WHERE message_id = ? AND thread_id = ?
            """,
            "update_memory_content_filter": """
                UPDATE chat_history_summary
                SET content_filter_results = ?
                WHERE message_id = ? AND thread_id = ?
            """,
            "insert_user": """
                INSERT INTO users (id, identifier, metadata, createdAt)
                VALUES (?, ?, ?, ?)
            """,
            "select_user": """
                SELECT id, identifier, metadata, createdAt
                FROM users
                WHERE identifier = ?
            """,
            "select_thread_messages": """
                SELECT TOP 5 user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function
                FROM (
                    SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                           content_filter_results, tool_calls, tool_call_id, tool_call_function,
                           ROW_NUMBER() OVER (ORDER BY timestamp DESC) as rn
                    FROM chat_history
                    WHERE thread_id = ?
                ) AS ranked
                WHERE rn <= 5
                ORDER BY timestamp ASC
            """,
            "select_thread_memory": """
                SELECT TOP 1 user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function
                FROM chat_history_summary
                WHERE thread_id = ?
                ORDER BY timestamp DESC
            """,
            "delete_thread": """
                DELETE FROM chat_history
                WHERE thread_id = ?
            """,
            "delete_thread_memory": """
                DELETE FROM chat_history_summary
                WHERE thread_id = ?
            """,
            "delete_user_memory": """
                DELETE FROM chat_history_summary
                WHERE user_id = ?
            """,
        }
        return queries.get(query_type, "")

    def execute_sql(self, sql, params=[], expect_results=True):
        """Legacy method for backward compatibility."""
        return self._execute_sql(sql, params, expect_results)

    def _create_tables(self):
        """Legacy method for backward compatibility. Tables are now created via base class."""
        pass

    async def _get_user_by_id(self, user_id: str) -> IChatHistoryRepository.User | None:
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT id, identifier, metadata, createdAt FROM users WHERE id = ?""",
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return IChatHistoryRepository.User(
                id=row[0], identifier=row[1], metadata=row[2], createdAt=row[3]
            )
        return None

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str]
    ) -> Optional[List[IChatHistoryRepository.ThreadDict]]:
        # This is a simplified implementation
        # In a full implementation, you'd join with threads table and return proper thread data
        return []

    async def get_thread(self, thread_id: str) -> list[IChatHistoryRepository.Thread]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, createdAt, name, userId, userIdentifier, tags, metadata
            FROM threads
            WHERE id = ?
        """,
            (thread_id,),
        )
        rows = cursor.fetchall()
        cursor.close()

        return [
            IChatHistoryRepository.Thread(
                id=row[0],
                createdAt=row[1],
                name=row[2],
                userId=row[3],
                userIdentifier=row[4],
                tags=row[5],
                metadata=row[6],
            )
            for row in rows
        ]

    async def add_step(self, step_dict: IChatHistoryRepository.StepDict):
        print("Creating step: ", step_dict)

        # If disableFeedback is not provided, default to False
        step_dict["disableFeedback"] = step_dict.get("disableFeedback", False)

        step_dict["showInput"] = (
            str(step_dict.get("showInput", "")).lower()
            if "showInput" in step_dict
            else None
        )
        parameters = {
            key: value
            for key, value in step_dict.items()
            if value is not None and not (isinstance(value, dict) and not value)
        }
        parameters["metadata"] = json.dumps(step_dict.get("metadata", {}))
        parameters["generation"] = json.dumps(step_dict.get("generation", {}))

        columns = ", ".join(f"[{key}]" for key in parameters.keys())
        values = ", ".join("?" for key in parameters.keys())
        query = f"""
            INSERT INTO steps ({columns})
            VALUES ({values});
        """
        self.execute_sql(
            sql=query, params=tuple(parameters.values()), expect_results=False
        )

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        print("Updating thread: ", thread_id)
        user_identifier = None
        if user_id:
            print("Getting user identifier for user_id: ", user_id)
            user = await self._get_user_by_id(user_id)
            if user:
                user_identifier = user.identifier

        data = {
            "id": thread_id,
            "createdAt": (self.get_now() if metadata is None else None),
            "name": (
                name
                if name is not None
                else (metadata.get("name") if metadata and "name" in metadata else None)
            ),
            "userId": user_id,
            "userIdentifier": user_identifier,
            "tags": json.dumps(tags) if tags else None,
            "metadata": json.dumps(metadata) if metadata else None,
        }

        parameters = {key: value for key, value in data.items() if value is not None}

        columns = ", ".join(f"[{key}]" for key in parameters.keys())
        values = ", ".join("?" for key in parameters.keys())
        updates = ", ".join(f"[{key}] = ?" for key in parameters.keys() if key != "id")

        # Use MERGE for upsert in SQL Server
        query = f"""
            MERGE threads AS target
            USING (SELECT ? as id) AS source ON target.id = source.id
            WHEN MATCHED THEN
                UPDATE SET {updates}
            WHEN NOT MATCHED THEN
                INSERT ({columns})
                VALUES ({values});
        """

        # Prepare parameters for MERGE statement
        merge_params = (
            [thread_id] + list(parameters.values())[1:] + list(parameters.values())
        )

        self.execute_sql(sql=query, params=merge_params, expect_results=False)

        return ""

    async def update_memory(self) -> None:
        cursor = self.connection.cursor()

        # Create a temporary table for the latest records
        cursor.execute("""
            SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                   content_filter_results, tool_calls, tool_call_id, tool_call_function
            INTO #latest_chat_history
            FROM (
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function,
                       ROW_NUMBER() OVER (PARTITION BY thread_id ORDER BY timestamp DESC) AS row_num
                FROM chat_history_summary
            ) AS LatestRecords
            WHERE row_num = 1
        """)

        # Clear the original table
        cursor.execute("DELETE FROM chat_history_summary")

        # Insert the latest records back into the original table
        cursor.execute("""
            INSERT INTO chat_history_summary (user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                                              content_filter_results, tool_calls, tool_call_id, tool_call_function)
            SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                   content_filter_results, tool_calls, tool_call_id, tool_call_function
            FROM #latest_chat_history
        """)

        # Drop the temporary table
        cursor.execute("DROP TABLE #latest_chat_history")
        cursor.close()
