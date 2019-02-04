"""Tests for service"""
import json
import jsend
import requests


def test_default_error():
    """Test default error response"""
    response = requests.get('http://localhost:8000/some_page_that_does_not_exist')

    assert response.status_code == 404

    expected_msg_error = jsend.error('404 - Not Found')
    assert json.loads(response.content) == expected_msg_error

def test_welcome_message():
    """Test welcome message response"""
    response = requests.get('http://localhost:8000/welcome')

    assert response.status_code == 200

    expected_msg = jsend.success({'message': 'Welcome'})
    assert json.loads(response.content) == expected_msg
