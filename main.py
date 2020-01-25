from fastapi.openapi.utils import get_openapi

from excel_uploader import models
from excel_uploader.database import SessionLocal, engine
from excel_uploader.resources import router

from fastapi import FastAPI

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)
app.openapi_schema = get_openapi(
        title="Excel File Uploader",
        version="1.0.0",
        description="A basic api for uploading and retrieving excel files",
        routes=app.routes,
    )