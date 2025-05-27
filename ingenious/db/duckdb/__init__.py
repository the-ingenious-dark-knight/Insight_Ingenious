import os
import sqlite3
import uuid
from datetime import datetime

import ingenious.config.config as Config
from ingenious.db.chat_history_repository import IChatHistoryRepository
from ingenious.models.message import Message


class duckdb_ChatHistoryRepository(IChatHistoryRepository):
    def __init__(self, config: Config.Config):
        db_path = config.chat_history.database_path
        self.connection = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    user_id TEXT,
                    thread_id TEXT,
                    message_id TEXT,
                    positive_feedback BOOLEAN,
                    timestamp TEXT,
                    role TEXT,
                    content TEXT,
                    content_filter_results TEXT,
                    tool_calls TEXT,
                    tool_call_id TEXT,
                    tool_call_function TEXT
                )
            """)

    async def add_message(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()

        with self.connection:
            self.connection.execute(
                """
                INSERT INTO chat_history (
                                    user_id,
                                    thread_id,
                                    message_id,
                                    positive_feedback,
                                    timestamp,
                                    role,
                                    content,
                                    content_filter_results,
                                    tool_calls,
                                    tool_call_id,
                                    tool_call_function)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    message.user_id,
                    message.thread_id,
                    message.message_id,
                    message.positive_feedback,
                    message.timestamp,
                    message.role,
                    message.content,
                    message.content_filter_results,
                    message.tool_calls,
                    message.tool_call_id,
                    message.tool_call_function,
                ),
            )

        return message.message_id

    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content, content_filter_results, tool_calls, tool_call_id, tool_call_function
            FROM chat_history
            WHERE id = ? AND thread_id = ?
        """,
            (message_id, thread_id),
        )
        row = cursor.fetchone()
        if row:
            return Message(
                user_id=row[0],
                thread_id=row[1],
                message_id=row[2],
                positive_feedback=row[3],
                timestamp=row[4],
                role=row[5],
                content=row[6],
                content_filter_results=row[7],
                tool_calls=row[8],
                tool_call_id=row[9],
                tool_call_function=row[10],
            )
        return None

    async def get_thread_messages(self, thread_id: str) -> list[Message]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content, content_filter_results, tool_calls, tool_call_id, tool_call_function
            FROM chat_history
            WHERE thread_id = ?
            ORDER BY timestamp
        """,
            (thread_id,),
        )
        rows = cursor.fetchall()
        return [
            Message(
                user_id=row[0],
                thread_id=row[1],
                message_id=row[2],
                positive_feedback=row[3],
                timestamp=row[4],
                role=row[5],
                content=row[6],
                content_filter_results=row[7],
                tool_calls=row[8],
                tool_call_id=row[9],
                tool_call_function=row[10],
            )
            for row in rows
        ]

    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        with self.connection:
            self.connection.execute(
                """
                UPDATE chat_history
                SET positive_feedback = ?
                WHERE id = ? AND thread_id = ?
            """,
                (positive_feedback, message_id, thread_id),
            )

    async def update_message_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        with self.connection:
            self.connection.execute(
                """
                UPDATE chat_history
                SET content_filter_results = ?
                WHERE id = ? AND thread_id = ?
            """,
                (str(content_filter_results), message_id, thread_id),
            )

    async def delete_thread(self, thread_id: str) -> None:
        with self.connection:
            self.connection.execute(
                """
                DELETE FROM chat_history
                WHERE thread_id = ?
            """,
                (thread_id,),
            )
