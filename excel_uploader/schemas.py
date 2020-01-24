from typing import List
from pydantic import BaseModel
from uuid import UUID

class ExcelFileSchema(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True

class MessageSchema(BaseModel):
    message: str