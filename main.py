from excel_uploader import models
from excel_uploader.database import SessionLocal, engine
from excel_uploader.resources import router

from fastapi import FastAPI

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)
