import os
from pytest import fixture
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from excel_uploader.repositories import FileRepository
from excel_uploader import resources, models
from main import app


@fixture
def client():
    return TestClient(app)


@fixture
def mock_files_payload():
    return [{"id": "6da0705f-a8aa-4730-a7c2-c5db85f57ca8", "name": "test"}]


@fixture
def mock_get_files(monkeypatch, mock_files_payload):
    monkeypatch.setattr(FileRepository, "get_files", lambda *args: mock_files_payload)


@fixture
def mock_file_storage_location(monkeypatch):
    monkeypatch.setattr(
        FileRepository,
        "PATH_TO_FILE_STORAGE",
        f"{os.path.dirname(os.path.abspath(__file__))}/resources/storage/",
    )


@fixture
def test_session():
    SQLALCHEMY_DATABASE_URL = "sqlite://"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    models.Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session()


@fixture
def db_session(test_session):
    try:
        db = test_session
        yield db
    finally:
        db.close()


@fixture
def mock_SessionLocal(monkeypatch, db_session):
    monkeypatch.setattr(resources, "get_db", lambda: db_session)
