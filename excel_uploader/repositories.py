from sqlalchemy.orm import Session
from .models import ExcelFile
from uuid import UUID, uuid4
import os
from sqlalchemy.orm.exc import NoResultFound
from fastapi import UploadFile
import openpyxl


class FileRepository:
    model = ExcelFile
    PATH_TO_FILE_STORAGE = f"{os.path.dirname(os.path.abspath(__file__))}/../storage/"

    def get_files(self, db: Session):
        """Retrieves records of all files currently stored"""
        return db.query(self.model).all()

    def get_file_by_id(self, db: Session, id: UUID):
        """
        Retrieves a file from the file system by id.
        raises: FileNotFoundError, NoResultFound
        returns: File file_record, 
        """
        file_record = db.query(self.model).filter(self.model.id==id).one()
        file_path = f"{self.PATH_TO_FILE_STORAGE}{file_record.id}.xlsx"
        return file_record, file_path

    def store_file(self, db: Session, file: UploadFile):
        file_record = self.model(id=uuid4(), name=file.filename)
        xl = openpyxl.load_workbook(file.file._file) # type: ignore
        xl.save(f"{self.PATH_TO_FILE_STORAGE}{file_record.id}.xlsx")
        db.add(file_record)
        db.commit()
        return file_record