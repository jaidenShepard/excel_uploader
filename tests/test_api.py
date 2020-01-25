import glob
import os
import json
from unittest.mock import patch
from pytest import mark
from excel_uploader.models import ExcelFile
import uuid


@mark.usefixtures("mock_SessionLocal")
class TestAPI:
    RESOURCE_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/resources/"

    @classmethod
    def teardown_class(cls):
        # clean up files created curing test
        filelist = glob.glob(cls.RESOURCE_PATH + "storage/*.xlsx")
        for file in filelist:
            # keeps our test file
            if (
                file
                != f"{cls.RESOURCE_PATH}storage/6da0705f-a8aa-4730-a7c2-c5db85f57ca8.xlsx"
            ):
                os.remove(file)

    def test_unknown_endpoint_returns_404(self, client):
        response = client.get("/fake_endpoint")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}

    def test_can_get_list_endpoint_exists(self, client):
        response = client.get("/files")
        assert response.status_code == 200

    def test_get_list_of_files_returns_expected_payload(
        self, client, mock_get_files, mock_files_payload
    ):
        response = client.get("/files")
        assert response.json() == mock_files_payload

    def test_can_upload_file(self, client, mock_file_storage_location):
        test_file = open(self.RESOURCE_PATH + "under_1mb.xlsx", "rb")
        resp = client.post("/files", files={"upload": test_file})
        assert resp.status_code == 201

        data = json.loads(resp.text)

        assert os.path.exists(f"{self.RESOURCE_PATH}/storage/{data['id']}.xlsx")

    def test_file_upload_fails_if_too_large(self, client):
        test_file = open(self.RESOURCE_PATH + "over_1mb.xlsx", "rb")
        resp = client.post("/files", files={"upload": test_file})
        assert resp.status_code == 400
        data = json.loads(resp.text)
        assert data["message"] == "File too large, limit is 1.0MB"

    def test_file_upload_fails_if_invalid_file_type(self, client):
        test_file = open(self.RESOURCE_PATH + "invalid_type.txt", "rb")
        resp = client.post("/files", files={"upload": test_file})
        assert resp.status_code == 400
        data = json.loads(resp.text)
        assert data["message"] == f"Invalid file type. Only .xlsx accepted"

    def test_file_upload_fails_if_invalid_file(self, client):
        test_file = open(self.RESOURCE_PATH + "invalid.xlsx", "r")
        resp = client.post("/files", files={"upload": test_file})
        assert resp.status_code == 400
        data = json.loads(resp.text)
        assert (
            data["message"] == "Invalid file. This file appears to not be a valid .xlsx"
        )

    def test_can_retrieve_file(self, client, db_session):
        db_session.add(
            ExcelFile(
                id=uuid.UUID("6da0705f-a8aa-4730-a7c2-c5db85f57ca8"), name="test.xlsx"
            )
        )
        db_session.commit()

        resp = client.get("/files/6da0705f-a8aa-4730-a7c2-c5db85f57ca8")
        assert resp.status_code == 200
        assert type(resp.content) == bytes

    def test_get_file_with_invalid_id_fails(self, client, db_session):
        db_session.add(
            ExcelFile(
                id=uuid.UUID("6da0705f-a8aa-4730-a7c2-c5db85f57ca8"), name="test.xlsx"
            )
        )
        db_session.commit()

        resp = client.get(f"/files/{uuid.uuid4()}")
        assert resp.status_code == 404
