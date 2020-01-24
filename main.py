from fastapi import FastAPI
from excel_uploader.resources import router

app = FastAPI()
app.include_router(router)