from pydantic import BaseModel


class Event(BaseModel):
    identifier: str
    event_type: str
    file_name: str
    response_content: str