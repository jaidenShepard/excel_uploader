from typing import List
from uuid import UUID

from pydantic import BaseModel


class ExcelFileSchema(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


class MessageSchema(BaseModel):
    message: str
