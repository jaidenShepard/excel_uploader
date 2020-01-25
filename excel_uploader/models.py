from uuid import UUID

from sqlalchemy import Column, String
import sqlalchemy.types as types

from .database import Base


class UUIDType(types.TypeDecorator):
    """
    Defines a custom UUID column type. Since sqlite doesn't support UUIDs, we need to 
    convert the UUID to a string when inserting, and convert it back into a UUID when
    reading from the database.
    """

    impl = types.String

    def process_bind_param(self, value: UUID, dialect):
        return str(value)

    def process_result_value(self, value: str, dialect):
        return UUID(value)


class ExcelFile(Base):
    __tablename__ = "files"
    id = Column(UUIDType, primary_key=True, index=True)
    name = Column(String, nullable=False)
