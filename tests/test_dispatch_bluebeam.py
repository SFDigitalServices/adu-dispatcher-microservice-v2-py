# pylint: disable=redefined-outer-name
"""Tests for dispatch_bluebeam """
import json
from unittest.mock import patch
import pytest
from falcon import testing

import service.microservice
from service.resources.dispatch_bluebeam import DispatchBluebeam

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

@pytest.fixture
def mock_env_access_key(monkeypatch):
    """ mock environment access key """
    monkeypatch.setenv("ACCESS_KEY", CLIENT_HEADERS["ACCESS_KEY"])

def test_dispatch_bluebeam_error(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """ Test dispatch email in error state """
    response = client.simulate_post(
        '/bluebeam/webhook',
        body=json.dumps({})
        )
    assert response.status_code == 500

    response = client.simulate_post(
        '/bluebeam/submission',
        body=json.dumps({})
        )
    assert response.status_code == 500

def test_trigger_bluebeam_submission():
    """ Test trigger_bluebeam_submission """
    mock_json = {"submission_id": 1234}
    with patch('service.resources.dispatch_bluebeam.requests.post') as mock_bb_post:
        mock_bb_post.return_value.status_code = 200
        mock_bb_post.return_value.json.return_value = mock_json

        assert mock_json == DispatchBluebeam.trigger_bluebeam_submission("123", True)
