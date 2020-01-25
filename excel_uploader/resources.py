from tempfile import SpooledTemporaryFile
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Query, UploadFile, File, Depends
from starlette.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from .database import SessionLocal
from .exceptions import *
from .schemas import ExcelFileSchema, MessageSchema
from .repositories import FileRepository

router = APIRouter()
repository = FileRepository()

EXCEL_FILE_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

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
    db: Session = Depends(get_db),
):
    """
    Retrieves a list of available files
    """
    return repository.get_files(db)


@router.get(
    "/files/{file_uuid}",
    responses={
        404: {"model": MessageSchema, "description": "The item was not found"},
        200: {"content": {EXCEL_FILE_MEDIA_TYPE: {}}},
    },
)
async def get_file_for_download(file_uuid: UUID, db: Session = Depends(get_db)):
    """
    Retrieves a file for download
    """
    try:
        file_record, file_path = repository.get_file_by_id(db, file_uuid)
        return FileResponse(
            file_path, filename=file_record.name, media_type=EXCEL_FILE_MEDIA_TYPE,
        )
    except (FileNotFoundError, NoResultFound):
        return JSONResponse(
            status_code=404,
            content={"message": f"Could not find file with id {file_uuid}"},
        )


@router.post(
    "/files",
    status_code=201,
    response_model=ExcelFileSchema,
    responses={
        400: {"model": MessageSchema, "description": "Invalid Upload"},
        201: {"model": ExcelFileSchema},
    },
)
async def upload_file(
    upload: UploadFile = File(default=None), db: Session = Depends(get_db)
):
    try:
        return await repository.store_file(db, upload)
    except (FileTooLargeException, InvalidFileException, InvalidFileTypeException) as e:
        return JSONResponse(status_code=400, content={"message": str(e)})
