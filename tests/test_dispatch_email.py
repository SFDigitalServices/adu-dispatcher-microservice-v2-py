# pylint: disable=redefined-outer-name
"""Tests for dispatch_email """
import os
import json
from unittest.mock import patch
import pytest
from falcon import testing
import service.microservice
from common import assert_mock

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service())

def test_dispatch_email_error(client):
    """ Test dispatch email in error state """
    response = client.simulate_post('/email')
    assert response.status_code == 500

def test_dispatch_email_exception(client):
    """ Test dispatch email in exception state """
    client.simulate_post('/email', body=json.dumps({"test":"test"}))

def test_dispatch_email(client):
    """ Test Create Record """

    with open('tests/mocks/airtable_row.json', 'r') as file_obj:
        airtable_row = json.load(file_obj)
    assert airtable_row

    with patch('service.modules.common.Airtable.get') as mock:
        mock.return_value = airtable_row

        with open('tests/mocks/dispatch_email_post.json', 'r') as file_obj:
            mock_post = json.load(file_obj)
        assert mock_post

        with open('tests/mocks/dispatch_email_response.json', 'r') as file_obj:
            mock_response = json.load(file_obj)
        assert mock_response

        mock_post['token'] = os.environ.get('EMAIL_TOKEN')

        if mock_post:
            response = client.simulate_post(
                '/email',
                body=json.dumps(mock_post))
            assert response.status_code == 200
            content = json.loads(response.content)

            assert content
            assert_mock(mock_response, content)
