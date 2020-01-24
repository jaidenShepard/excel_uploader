from main import app
from pytest import fixture
from starlette.testclient import TestClient
from excel_uploader.repositories import FileRepository

@fixture
def client():
    return TestClient(app)

@fixture
def mock_files_payload():
    return [{"id": "6da0705f-a8aa-4730-a7c2-c5db85f57ca8", "name": "test"}]

@fixture
def mock_get_files(monkeypatch, mock_files_payload):
    monkeypatch.setattr(
        FileRepository, 
        "get_files", 
        lambda *args: mock_files_payload
    )