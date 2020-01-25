import os
from tempfile import SpooledTemporaryFile
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
import openpyxl

from .exceptions import (
    FileTooLargeException,
    InvalidFileException,
    InvalidFileTypeException,
)
from .models import ExcelFile

MB = 1000000


class FileRepository:
    model = ExcelFile
    PATH_TO_FILE_STORAGE = f"{os.path.dirname(os.path.abspath(__file__))}/../storage/"

    async def _validate_size_is_lte(self, file: UploadFile, size: int):
        """
        Validates that the give file is less than or equal to the given size
        """
        res = await file.read()
        if not len(res) <= size:
            raise FileTooLargeException(f"File too large, limit is {size/1000000}MB")

    def _validate_file_type(self, file: UploadFile, filetype: str):
        """
        Checks that the file extension matches the given file type
        """
        if not file.filename[-(len(filetype)) :] == filetype:
            raise InvalidFileTypeException(
                f"Invalid file type. Only {filetype} accepted"
            )

    def validate_is_valid_excel_file(self, file: SpooledTemporaryFile):
        """Attempts to load the excel file, if it fails, the file is invalid"""
        try:
            openpyxl.load_workbook(file._file)  # type: ignore
        except:
            return False
        return True

    def get_files(self, db: Session):
        """Retrieves records of all files currently stored"""
        return db.query(self.model).all()

    def get_file_by_id(self, db: Session, id: UUID):
        """
        Retrieves a file from the file system by id.
        raises: FileNotFoundError, NoResultFound
        returns: File file_record, 
        """
        file_record = db.query(self.model).filter(self.model.id == id).one()
        file_path = f"{self.PATH_TO_FILE_STORAGE}{file_record.id}.xlsx"
        return file_record, file_path

    async def store_file(self, db: Session, upload: UploadFile):
        """
        Validates and stores an uploaded file.
        raises: FileTooLargeException, InvalidFileTypeException, InvalidFileException
        returns: ExcelFile
        """
        await self._validate_size_is_lte(upload, MB)
        self._validate_file_type(upload, ".xlsx")
        file_record = self.model(id=uuid4(), name=upload.filename)

        try:
            xl = openpyxl.load_workbook(upload.file._file)  # type: ignore
            xl.save(f"{self.PATH_TO_FILE_STORAGE}{file_record.id}.xlsx")
        except IndexError:
            # openpyxl complains if there isn't a visible sheet, even if the
            # file saved successfully
            pass
        except:
            raise InvalidFileException(
                "Invalid file. This file appears to not be a valid .xlsx"
            )

        db.add(file_record)
        db.commit()
        return file_record
