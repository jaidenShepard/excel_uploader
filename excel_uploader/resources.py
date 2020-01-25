from fastapi import APIRouter, Query, UploadFile, File
from typing import List, Optional
from .schemas import ExcelFileSchema, MessageSchema
from fastapi import Depends
from .repositories import FileRepository
from .database import SessionLocal
from sqlalchemy.orm import Session
from uuid import UUID
from starlette.responses import FileResponse, JSONResponse
from sqlalchemy.orm.exc import NoResultFound
from tempfile import SpooledTemporaryFile

router = APIRouter()
repository = FileRepository()

EXCEL_FILE_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MB = 1000000

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def validate_size_is_lte(file: UploadFile, size: int):
    """
    Validates that the give file is less than or equal to the given size
    """
    res = await file.read()
    return len(res) <= size

def validate_file_type(file: UploadFile, filetype: str):
    """
    Checks that the file extension matches the given file type
    """
    return file.filename[-(len(filetype)):] == filetype

def validate_is_valid_excel_file(file: SpooledTemporaryFile):
    """Attempts to load the excel file, if it fails, the file is invalid"""
    try:
        openpyxl.load_workbook(file._file) # type: ignore
    except:
        return False
    return True

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
    "/files/{file_uuid}", 
    responses={
        404: {"model": MessageSchema, "description": "The item was not found"},
        200: {"content": {EXCEL_FILE_MEDIA_TYPE: {}}}
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
            content={"message": f"Could not find file with id {file_uuid}"}
        )

@router.post("/files", response_model=ExcelFileSchema)
async def upload_file(
    upload: UploadFile = File(default=None),
    db: Session = Depends(get_db)
):
    if not await validate_size_is_lte(upload, MB):
        return JSONResponse(
            status_code=400, 
            content={"message": "File too large, limit is 1MB"}
        )
    if not validate_file_type(upload, '.xlsx'):
        return JSONResponse(
            status_code=400, 
            content={"message": "Invalid file type. Only .xlsx accepted"}
        )
    # if not validate_is_valid_excel_file(upload.file): # type: ignore
    #     return JSONResponse(
    #         status_code=400, 
    #         content={
    #             "message": "Invalid file. This file appears to not be a valid .xlsx file"
    #         }
    #     )
    return repository.store_file(db, upload)