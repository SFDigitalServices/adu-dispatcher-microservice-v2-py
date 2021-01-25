# pylint: disable=redefined-outer-name
"""Tests for submission"""
import os
import json
from unittest.mock import patch
import pytest
from falcon import testing
import service.microservice
from common import assert_mock

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

@pytest.fixture()
def client():
    """ client fixture """
    CLIENT_HEADERS['ACCESS_KEY'] = os.environ.get('ACCESS_KEY')
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

def test_create_record_error(client):
    """ Test Create Record with error """

    with open('tests/mocks/submission_data.json', 'r') as file_obj:
        submission_data = json.load(file_obj)
    assert submission_data

    with patch('service.resources.submission.Submission.get_submssion_json') as mock:
        mock.return_value = submission_data

        with patch('service.resources.submission.Submission.create_submission_airtable') as mock:
            mock.return_value = {"id":123}

            with patch('service.modules.accela.Accela.send_record_to_accela') as mock:
                mock.return_value.status_code = 400
                mock.return_value.json.return_value = {}

                response = client.simulate_post(
                    '/submission',
                    body=json.dumps({"id":123}))
                assert response.status_code == 400
                content = json.loads(response.content)
                assert content

def test_create_record(client):
    """ Test Create Record """
    with open('tests/mocks/submission.json', 'r') as file_obj:
        mock_record = json.load(file_obj)
    assert mock_record

    if mock_record:
        with patch('service.modules.common.SendGridAPIClient.send') as mock:
            mock.return_value.status_code = 200
            mock.body = "test content"
            mock.headers = json.dumps({})

            response = client.simulate_post(
                '/submission',
                body=json.dumps(mock_record),
                headers={'X-Options':'EMAIL'})
            assert response.status_code == 200
            content = json.loads(response.content)
            assert content

            with open('tests/mocks/submission_response.json', 'r') as file_obj:
                mock_response = json.load(file_obj)
            assert mock_response
            assert_mock(mock_response, content)

def test_create_record_bluebeam(client):
    """ Test Create Record """
    with open('tests/mocks/submission.json', 'r') as file_obj:
        mock_record = json.load(file_obj)
    assert mock_record

    if mock_record:
        # pylint: disable=line-too-long
        with patch('service.resources.dispatch_bluebeam.DispatchBluebeam.trigger_bluebeam_submission') as mock_trigger:
            mock_trigger.return_value = True

            response = client.simulate_post(
                '/submission',
                body=json.dumps(mock_record),
                headers={'X-Options':'BLUEBEAM'})
            assert response.status_code == 200
            content = json.loads(response.content)
            assert content

            with open('tests/mocks/submission_response.json', 'r') as file_obj:
                mock_response = json.load(file_obj)
                del mock_response['data']['emails']
            assert mock_response
            assert_mock(mock_response, content)

            assert content['data']['airtable']['id']
            airtable_id = content['data']['airtable']['id']

            helper_test_dispatch_bluebeam_submission(client, airtable_id)
            helper_test_dispatch_bluebeam_webhook(client, airtable_id)

def helper_test_dispatch_bluebeam_webhook(client, airtable_id):
    """ Test bluebeam webhook """
    with open('tests/mocks/dispatch_bluebeam_webhook_post.json', 'r') as file_obj:
        mock_post = json.load(file_obj)
        assert mock_post

    with patch('service.modules.common.SendGridAPIClient.send') as mock:
        mock.return_value.status_code = 200
        mock.body = "test content"
        mock.headers = json.dumps({})

        response = client.simulate_post(
            '/bluebeam/webhook',
            params={'airtable_record_id': airtable_id, 'send_email': True},
            body=json.dumps(mock_post))
        assert response.status_code == 200
        content = json.loads(response.content)
        assert content

        with open('tests/mocks/dispatch_bluebeam_webhook_response.json', 'r') as file_obj:
            mock_response = json.load(file_obj)
        assert mock_response
        assert_mock(mock_response, content)

def helper_test_dispatch_bluebeam_submission(client, airtable_id):
    """ Test bluebeam submission """
    with open('tests/mocks/dispatch_bluebeam_submission_post.json', 'r') as file_obj:
        mock_post = json.load(file_obj)
        assert mock_post

    with patch('service.resources.dispatch_bluebeam.requests.post') as mock_bb_post:
        mock_bb_post.return_value.status_code = 200
        mock_bb_post.return_value.json.return_value = {"submission_id": 1234}

        with patch('service.modules.common.SendGridAPIClient.send') as mock_send:
            mock_send.return_value.status_code = 200
            mock_send.body = "test content"
            mock_send.headers = json.dumps({})

            response = client.simulate_post(
                '/bluebeam/submission',
                headers={'X-Options':'EMAIL'},
                body=json.dumps({'airtable_record_id': airtable_id}))
            assert response.status_code == 200
            content = json.loads(response.content)
            assert content
