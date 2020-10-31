# pylint: disable=redefined-outer-name
"""Tests for microservice"""
import os
import json
import pytest
from falcon import testing
import service.microservice

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

@pytest.fixture()
def client():
    """ client fixture """
    CLIENT_HEADERS['ACCESS_KEY'] = os.environ.get('ACCESS_KEY')
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

def test_create_record(client):
    """ Test Create Record """
    with open('tests/mocks/submission.json', 'r') as file_obj:
        mock_record = json.load(file_obj)

    assert mock_record

    if mock_record:
        response = client.simulate_post(
            '/submission',
            body=json.dumps(mock_record))
        assert response.status_code == 200
        content = json.loads(response.content)
        assert content
