import os
import sys
import uuid

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), './../'))
sys.path.append(parent_dir)

import ingenious.dependencies as deps
from ingenious.models.chat import ChatRequest, ChatResponse
import asyncio

from ingenious.utils.load_sample_data import sqlite_sample_db
test_db = sqlite_sample_db()
test_db.execute_sql('SELECT * FROM students_performance')


