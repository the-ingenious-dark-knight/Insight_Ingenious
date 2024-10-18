---

    weight: 5

---



# Repo Folder Structure

The `__init__.py` enables namespace packages, a feature where multiple directories can contribute to a single package. 
It essentially extends the package’s `__path__` to allow Python to combine code from different locations 
in the file system under the same package name.


``` powershell title="View the Folder Structure"
.
├── __init__.py
│   ├── __init__.cpython-312.pyc
│   └── dependencies.cpython-312.pyc
├── api
│   ├── __init__.py
│   └── routes
├── chainlit
│   └── datalayer.py
├── cli.py
├── config
│   ├── config.py
│   └── profile.py
├── core
│   ├── __init__.py
│   └── logging.py
├── db
│   ├── __init__.py
│   ├── chat_history_repository.py
│   ├── cosmos
│   ├── duckdb
│   └── sqlite
├── dependencies.py
├── errors
│   ├── __init__.py
│   ├── __pycache__
│   ├── content_filter_error.py
│   └── token_limit_exceeded_error.py
├── external_services
│   ├── __init__.py
│   ├── __pycache__
│   ├── openai_service.py
│   └── search_service.py
├── main.py
├── models
│   ├── __init__.py
│   ├── __pycache__
│   ├── chat.py
│   ├── database_client.py
│   ├── http_error.py
│   ├── message.py
│   ├── message_feedback.py
│   ├── search.py
│   └── tool_call_result.py
├── services
│   ├── __init__.py
│   ├── chat_service.py
│   ├── chat_services
│   ├── message_feedback_service.py
│   └── tool_service.py
└── utils
    ├── __init__.py
    ├── conversation_builder.py
    ├── prompt_templates.py
    └── token_counter.py
```

