from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Email(BaseModel):
    id: Optional[int] = None
    sender: str
    subject: str
    body: str
    timestamp: str
    category: Optional[str] = None
    action_items: Optional[str] = None

class Prompt(BaseModel):
    id: Optional[int] = None
    name: str
    content: str
    description: Optional[str] = ""

class Draft(BaseModel):
    id: Optional[int] = None
    email_id: Optional[int] = None
    subject: str
    body: str
    metadata: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    email_id: Optional[int] = None
    context: Optional[str] = None

class ProcessEmailsRequest(BaseModel):
    emails: List[Email]
