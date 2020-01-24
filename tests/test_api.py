from unittest.mock import patch

class TestAPI:
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
