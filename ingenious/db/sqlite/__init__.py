import json
import os
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from queue import Empty, Queue
from typing import Dict, List, Optional

import ingenious.config.config as Config
from ingenious.db.chat_history_repository import IChatHistoryRepository
from ingenious.models.message import Message


class ConnectionPool:
    """Thread-safe SQLite connection pool with health checks and retry logic."""

    def __init__(
        self,
        db_path: str,
        pool_size: int = 8,
        max_retries: int = 3,
        retry_delay: float = 0.1,
    ):
        self.db_path = db_path
        self.pool_size = pool_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._pool = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_connections = 0

        # Pre-populate the pool
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool with healthy connections."""
        for _ in range(self.pool_size):
            try:
                conn = self._create_connection()
                if self._is_connection_healthy(conn):
                    self._pool.put(conn)
                    self._created_connections += 1
                else:
                    conn.close()
            except Exception:
                # If we can't create initial connections, we'll create them on demand
                break

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with proper configuration."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0,
            isolation_level=None,  # autocommit mode
        )
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn

    def _is_connection_healthy(self, conn: sqlite3.Connection) -> bool:
        """Check if a connection is healthy by executing a simple query."""
        try:
            conn.execute("SELECT 1").fetchone()
            return True
        except Exception:
            return False

    @contextmanager
    def get_connection(self):
        """Context manager to get a connection from the pool."""
        conn = None
        retry_count = 0

        while retry_count <= self.max_retries:
            try:
                # Try to get a connection from the pool
                try:
                    conn = self._pool.get(timeout=5.0)
                except Empty:
                    # Pool is empty, create a new connection
                    with self._lock:
                        if (
                            self._created_connections < self.pool_size * 2
                        ):  # Allow some overflow
                            conn = self._create_connection()
                            self._created_connections += 1
                        else:
                            # Wait a bit and try again
                            time.sleep(self.retry_delay)
                            retry_count += 1
                            continue

                # Check if connection is healthy
                if conn and self._is_connection_healthy(conn):
                    try:
                        yield conn
                        # Return connection to pool if still healthy
                        if self._is_connection_healthy(conn):
                            self._pool.put_nowait(conn)
                        else:
                            conn.close()
                            with self._lock:
                                self._created_connections -= 1
                        return
                    except Exception as e:
                        # If there was an error using the connection, close it
                        if conn:
                            try:
                                conn.close()
                            except Exception:
                                pass
                            with self._lock:
                                self._created_connections -= 1
                        raise e
                else:
                    # Connection is unhealthy, close it and retry
                    if conn:
                        try:
                            conn.close()
                        except Exception:
                            pass
                        with self._lock:
                            self._created_connections -= 1

                    retry_count += 1
                    if retry_count <= self.max_retries:
                        time.sleep(
                            self.retry_delay * retry_count
                        )  # Exponential backoff

            except Exception as e:
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    with self._lock:
                        self._created_connections -= 1

                retry_count += 1
                if retry_count <= self.max_retries:
                    time.sleep(self.retry_delay * retry_count)
                else:
                    raise RuntimeError(
                        f"Failed to get database connection after {self.max_retries} retries: {e}"
                    )

        raise RuntimeError(
            f"Failed to get database connection after {self.max_retries} retries"
        )

    def close_all(self):
        """Close all connections in the pool."""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except (Empty, Exception):
                break

        with self._lock:
            self._created_connections = 0


class sqlite_ChatHistoryRepository(IChatHistoryRepository):
    def __init__(self, config: Config.Config):
        self.db_path = config.chat_history.database_path
        # Check if the directory exists, if not, create it
        db_dir_check = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir_check):
            os.makedirs(db_dir_check)

        # Initialize connection pool
        pool_size = getattr(config.chat_history, "connection_pool_size", 8)
        self.pool = ConnectionPool(self.db_path, pool_size=pool_size)

        # Create tables using a connection from the pool
        self._create_table()

    def __del__(self):
        """Destructor to ensure connections are properly closed."""
        try:
            self.close()
        except Exception:
            pass

    def close(self):
        """Close all connections in the pool."""
        if hasattr(self, "pool"):
            self.pool.close_all()

    def execute_sql(self, sql, params=[], expect_results=True):
        try:
            with self.pool.get_connection() as connection:
                cursor = connection.cursor()
                # print("Executing SQL: ", sql)
                # print("Params: ", params)

                if expect_results:
                    res = cursor.execute(sql, params)
                    rows = res.fetchall()
                    result = [dict(row) for row in rows]
                    return result
                else:
                    connection.execute(sql, params)
                    connection.commit()

        except sqlite3.Error as e:
            # Display the exception
            print(e)

    def _create_table(self):
        with self.pool.get_connection() as connection:
            connection.execute("""
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
                );
            """)

            connection.execute("""
                            CREATE TABLE IF NOT EXISTS chat_history_summary (
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
                            );
                        """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    "id" UUID PRIMARY KEY,
                    "identifier" TEXT NOT NULL UNIQUE,
                    "metadata" JSONB NOT NULL,
                    "createdAt" TEXT
                );
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS threads (
                    "id" UUID PRIMARY KEY,
                    "createdAt" TEXT,
                    "name" TEXT,
                    "userId" UUID,
                    "userIdentifier" TEXT,
                    "tags" TEXT[],
                    "metadata" JSONB,
                    FOREIGN KEY ("userId") REFERENCES users("id") ON DELETE CASCADE
                );
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS steps (
                    "id" UUID PRIMARY KEY,
                    "name" TEXT NOT NULL,
                    "type" TEXT NOT NULL,
                    "threadId" UUID NOT NULL,
                    "parentId" UUID,
                    "disableFeedback" BOOLEAN NOT NULL,
                    "streaming" BOOLEAN NOT NULL,
                    "waitForAnswer" BOOLEAN,
                    "isError" BOOLEAN,
                    "metadata" JSONB,
                    "tags" TEXT[],
                    "input" TEXT,
                    "output" TEXT,
                    "createdAt" TEXT,
                    "start" TEXT,
                    "end" TEXT,
                    "generation" JSONB,
                    "showInput" TEXT,
                    "language" TEXT,
                    "indent" INT
                );
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS elements (
                    "id" UUID PRIMARY KEY,
                    "threadId" UUID,
                    "type" TEXT,
                    "url" TEXT,
                    "chainlitKey" TEXT,
                    "name" TEXT NOT NULL,
                    "display" TEXT,
                    "objectKey" TEXT,
                    "size" TEXT,
                    "page" INT,
                    "language" TEXT,
                    "forId" UUID,
                    "mime" TEXT
                );

            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS feedbacks (
                    "id" UUID PRIMARY KEY,
                    "forId" UUID NOT NULL,
                    "threadId" UUID NOT NULL,
                    "value" INT NOT NULL,
                    "comment" TEXT
                );
            """)

    async def _get_user_by_id(self, user_id: str) -> IChatHistoryRepository.User | None:
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """SELECT id, identifier, metadata, createdAt FROM users WHERE id = ?""",
                (user_id,),
            )
            row = cursor.fetchone()
            if row:
                return IChatHistoryRepository.User(
                    id=row[0], identifier=row[1], metadata=row[2], createdAt=row[3]
                )
            return None

    async def add_memory(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()

        with self.pool.get_connection() as connection:
            connection.execute(
                """
                INSERT INTO chat_history_summary (
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

    async def add_message(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()

        with self.pool.get_connection() as connection:
            connection.execute(
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

    async def add_user(
        self, identifier, metadata: dict = {}
    ) -> IChatHistoryRepository.User:
        now = self.get_now()
        new_id = str(uuid.uuid4())
        with self.pool.get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (
                                    id,
                                    identifier,
                                    metadata,
                                    createdAt
                                    )
                VALUES (?, ?, ?, ?)
            """,
                (new_id, identifier, json.dumps(metadata), now),
            )
        return IChatHistoryRepository.User(
            id=uuid.UUID(new_id),
            identifier=identifier,
            metadata=metadata,
            createdAt=self.get_now_as_string(),
        )

    async def get_user(self, identifier) -> IChatHistoryRepository.User | None:
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    identifier,
                    metadata,
                    createdAt
                FROM users
                WHERE identifier = ?
            """,
                (identifier,),
            )
            row = cursor.fetchone()
            if row:
                # Convert the dictionary to an object
                return IChatHistoryRepository.User(
                    id=row[0], identifier=row[1], metadata=row[2], createdAt=row[3]
                )
            else:
                usr = await self.add_user(identifier)
                return usr

    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content, content_filter_results, tool_calls, tool_call_id, tool_call_function
                FROM chat_history
                WHERE message_id = ? AND thread_id = ?
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

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str]
    ) -> Optional[List[IChatHistoryRepository.ThreadDict]]:
        """Fetch all user threads up to self.user_thread_limit, or one thread by id if thread_id is provided."""
        if thread_id is None:
            user_threads_query = """
                SELECT
                    "id" AS thread_id,
                    "createdAt" AS thread_createdat,
                    "name" AS thread_name,
                    "userId" AS user_id,
                    "userIdentifier" AS user_identifier,
                    "tags" AS thread_tags,
                    "metadata" AS thread_metadata
                FROM threads
                WHERE "userIdentifier" = ?
                ORDER BY "createdAt" DESC
                LIMIT ?
            """

            user_threads = self.execute_sql(user_threads_query, (identifier, 100))
        else:
            user_threads_query = """
                SELECT
                    "id" AS thread_id,
                    "createdAt" AS thread_createdat,
                    "name" AS thread_name,
                    "userId" AS user_id,
                    "userIdentifier" AS user_identifier,
                    "tags" AS thread_tags,
                    "metadata" AS thread_metadata
                FROM threads
                WHERE "userIdentifier" = ? AND "id" = ?
                ORDER BY "createdAt" DESC
                LIMIT ?
            """

            user_threads = self.execute_sql(
                user_threads_query, (identifier, thread_id, 100)
            )

        if not isinstance(user_threads, list):
            return None
        if not user_threads:
            return []
        else:
            thread_ids_list = []
            for thread in user_threads:
                thread_ids_list.append(str(thread["thread_id"]))

            # Create parameterized placeholders for IN clause
            thread_ids_placeholders = ",".join("?" * len(thread_ids_list))

        steps_feedbacks_query = f"""
            SELECT
                s."id" AS step_id,
                s."name" AS step_name,
                s."type" AS step_type,
                s."threadId" AS step_threadid,
                s."parentId" AS step_parentid,
                s."streaming" AS step_streaming,
                s."waitForAnswer" AS step_waitforanswer,
                s."isError" AS step_iserror,
                s."metadata" AS step_metadata,
                s."tags" AS step_tags,
                s."input" AS step_input,
                s."output" AS step_output,
                s."createdAt" AS step_createdat,
                s."start" AS step_start,
                s."end" AS step_end,
                s."generation" AS step_generation,
                s."showInput" AS step_showinput,
                s."language" AS step_language,
                s."indent" AS step_indent,
                f."value" AS feedback_value,
                f."comment" AS feedback_comment,
                f."id" AS feedback_id
            FROM steps s LEFT JOIN feedbacks f ON s."id" = f."forId"
            WHERE s."threadId" IN ({thread_ids_placeholders})
            ORDER BY s."createdAt" ASC
        """
        steps_feedbacks = self.execute_sql(steps_feedbacks_query, thread_ids_list)

        elements_query = f"""
            SELECT
                e."id" AS element_id,
                e."threadId" as element_threadid,
                e."type" AS element_type,
                e."chainlitKey" AS element_chainlitkey,
                e."url" AS element_url,
                e."objectKey" as element_objectkey,
                e."name" AS element_name,
                e."display" AS element_display,
                e."size" AS element_size,
                e."language" AS element_language,
                e."page" AS element_page,
                e."forId" AS element_forid,
                e."mime" AS element_mime
            FROM elements e
            WHERE e."threadId" IN ({thread_ids_placeholders})
        """
        elements = self.execute_sql(elements_query, thread_ids_list)

        thread_dicts = {}
        for thread in user_threads:
            thread_id = thread["thread_id"]
            if thread_id is not None:
                thread_dicts[thread_id] = IChatHistoryRepository.ThreadDict(
                    id=thread_id,
                    createdAt=thread["thread_createdat"],
                    name=thread["thread_name"],
                    userId=thread["user_id"],
                    userIdentifier=thread["user_identifier"],
                    tags=thread["thread_tags"],
                    metadata=thread[
                        "thread_id"
                    ],  # TODO: this gives NONE json.loads(thread["thread_metadata"]),
                    steps=[],
                    elements=[],
                )
        # Process steps_feedbacks to populate the steps in the corresponding ThreadDict
        if isinstance(steps_feedbacks, list):
            for step_feedback in steps_feedbacks:
                thread_id = step_feedback["step_threadid"]
                if thread_id is not None:
                    feedback = None
                    if step_feedback["feedback_value"] is not None:
                        feedback = IChatHistoryRepository.FeedbackDict(
                            forId=step_feedback["step_id"],
                            id=step_feedback.get("feedback_id"),
                            value=step_feedback["feedback_value"],
                            comment=step_feedback.get("feedback_comment"),
                        )
                    step_dict = IChatHistoryRepository.StepDict(
                        id=step_feedback["step_id"],
                        name=step_feedback["step_name"],
                        type=step_feedback["step_type"],
                        threadId=thread_id,
                        parentId=step_feedback.get("step_parentid"),
                        streaming=step_feedback.get("step_streaming", False),
                        waitForAnswer=step_feedback.get("step_waitforanswer"),
                        isError=step_feedback.get("step_iserror"),
                        metadata=(
                            step_feedback["step_metadata"]
                            if step_feedback.get("step_metadata") is not None
                            else {}
                        ),
                        tags=step_feedback.get("step_tags"),
                        input=(
                            step_feedback.get("step_input", "")
                            if step_feedback.get("step_showinput")
                            not in [None, "false"]
                            else ""
                        ),
                        output=step_feedback.get("step_output", ""),
                        createdAt=step_feedback.get("step_createdat"),
                        start=step_feedback.get("step_start"),
                        end=step_feedback.get("step_end"),
                        generation=step_feedback.get("step_generation"),
                        showInput=step_feedback.get("step_showinput"),
                        language=step_feedback.get("step_language"),
                        indent=step_feedback.get("step_indent"),
                        feedback=feedback,
                    )
                    # Append the step to the steps list of the corresponding ThreadDict
                    thread_dicts[thread_id]["steps"].append(step_dict)

        if isinstance(elements, list):
            for element in elements:
                thread_id = element["element_threadid"]
                if thread_id is not None:
                    element_dict = IChatHistoryRepository.ElementDict(
                        id=element["element_id"],
                        threadId=thread_id,
                        type=element["element_type"],
                        chainlitKey=element.get("element_chainlitkey"),
                        url=element.get("element_url"),
                        objectKey=element.get("element_objectkey"),
                        name=element["element_name"],
                        display=element["element_display"],
                        size=element.get("element_size"),
                        language=element.get("element_language"),
                        autoPlay=element.get("element_autoPlay"),
                        playerConfig=element.get("element_playerconfig"),
                        page=element.get("element_page"),
                        forId=element.get("element_forid"),
                        mime=element.get("element_mime"),
                    )
                    thread_dicts[thread_id]["elements"].append(element_dict)  # type: ignore
        # print("Thread Dicts: ", thread_dicts)
        return list(thread_dicts.values())

    async def get_thread_messages(self, thread_id: str) -> list[Message]:
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT *
                FROM (
                    SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content, content_filter_results, tool_calls, tool_call_id, tool_call_function
                    FROM chat_history
                    WHERE thread_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 5
                ) AS last_five
                ORDER BY timestamp ASC;
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

    async def get_thread(self, thread_id: str) -> list[IChatHistoryRepository.Thread]:
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, createdAt, name, userId, userIdentifier, tags, metadata
                FROM threads
                WHERE id = ?
            """,
                (thread_id,),
            )
            rows = cursor.fetchall()
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

    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        with self.pool.get_connection() as connection:
            connection.execute(
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
        with self.pool.get_connection() as connection:
            connection.execute(
                """
                UPDATE chat_history
                SET content_filter_results = ?
                WHERE id = ? AND thread_id = ?
            """,
                (str(content_filter_results), message_id, thread_id),
            )

    async def delete_thread(self, thread_id: str) -> None:
        with self.pool.get_connection() as connection:
            connection.execute(
                """
                DELETE FROM chat_history
                WHERE thread_id = ?
            """,
                (thread_id,),
            )

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
        columns = ", ".join(f'"{key}"' for key in parameters.keys())
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
            "tags": tags,
            "metadata": json.dumps(metadata) if metadata else None,
        }
        parameters = {
            key: value for key, value in data.items() if value is not None
        }  # Remove keys with None values
        columns = ", ".join(f'"{key}"' for key in parameters.keys())
        values = ", ".join("?" for key in parameters.keys())
        updates = ", ".join(
            f'"{key}" = EXCLUDED."{key}"' for key in parameters.keys() if key != "id"
        )
        query = f"""
            INSERT INTO threads ({columns})
            VALUES ({values})
            ON CONFLICT ("id") DO UPDATE
            SET {updates};
        """
        self.execute_sql(
            sql=query, params=tuple(parameters.values()), expect_results=False
        )

        return ""

    async def update_memory(self) -> None:
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()

            # Create a temporary table for the latest records
            cursor.execute("""
                CREATE TEMP TABLE latest_chat_history AS
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function
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
                FROM latest_chat_history
            """)

            # Drop the temporary table
            cursor.execute("DROP TABLE latest_chat_history")

            cursor.close()

    async def get_memory(self, message_id: str, thread_id: str) -> Message | None:
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function
                FROM chat_history_summary
                WHERE thread_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """,
                (thread_id,),
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

    async def get_thread_memory(self, thread_id: str) -> list[Message]:
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function
                FROM chat_history_summary
                WHERE thread_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
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

    async def update_memory_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        with self.pool.get_connection() as connection:
            connection.execute(
                """
                UPDATE chat_history_summary
                SET positive_feedback = ?
                WHERE id = ? AND thread_id = ?
            """,
                (positive_feedback, message_id, thread_id),
            )

    async def update_memory_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        with self.pool.get_connection() as connection:
            connection.execute(
                """
                UPDATE chat_history_summary
                SET content_filter_results = ?
                WHERE id = ? AND thread_id = ?
            """,
                (str(content_filter_results), message_id, thread_id),
            )

    async def delete_thread_memory(self, thread_id: str) -> None:
        with self.pool.get_connection() as connection:
            connection.execute(
                """
                DELETE FROM chat_history_summary
                WHERE thread_id = ?
            """,
                (thread_id,),
            )

    async def delete_user_memory(self, user_id: str) -> None:
        with self.pool.get_connection() as connection:
            connection.execute(
                """
                DELETE FROM chat_history_summary
                WHERE user_id = ?
            """,
                (user_id,),
            )
