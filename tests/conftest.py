from main import app
from pytest import fixture
from starlette.testclient import TestClient

@fixture
def client():
    return TestClient(app)