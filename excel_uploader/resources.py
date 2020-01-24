from fastapi import APIRouter, Query
from typing import List, Optional
from .schemas import ExcelFileSchema, MessageSchema
from fastapi import Depends
from .repositories import FileRepository
from .database import SessionLocal
from sqlalchemy.orm import Session
from uuid import UUID
from starlette.responses import FileResponse, JSONResponse
from sqlalchemy.orm.exc import NoResultFound

router = APIRouter()
repository = FileRepository()

EXCEL_FILE_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/files", response_model=List[ExcelFileSchema])
def get_files(
    limit: Optional[int] = Query(
        None, gt=0, description="Limit the number of files to display"
    ),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of available files
    """
    return repository.get_files(db)

@router.get(
    "/files/{file_id}", 
    responses={
        404: {"model": MessageSchema, "description": "The item was not found"},
        200: {
            "content": {
                EXCEL_FILE_MEDIA_TYPE: {}
            }
        }
    }
)
async def get_file(
    file_uuid: UUID,
    db: Session = Depends(get_db)
):  
    """
    Retrieves a file for download
    """
    try:
        file_record, file_path = repository.get_file_by_id(db, file_uuid)
        return FileResponse(
                file_path,
                filename=file_record.name,
                media_type=EXCEL_FILE_MEDIA_TYPE,
            )
    except (FileNotFoundError, NoResultFound):
        return JSONResponse(
            status_code=404, 
            content={"message": "Could not find file with id {file_id}"}
        )
