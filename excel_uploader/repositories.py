from sqlalchemy.orm import Session
from .models import ExcelFile
from uuid import UUID
import os
from sqlalchemy.orm.exc import NoResultFound

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
