# pylint: disable=redefined-outer-name
"""Tests for common function """
from unittest.mock import patch
import pytest
import service.modules.common as common

def test_email_exception():
    """ test email function exception """
    with patch('service.modules.common.SendGridAPIClient.send') as mock:
        mock.return_value.status_code = 500
        mock.side_effect = ValueError('ERROR_TEST')

        with pytest.raises(Exception):
            common.email("test@test", "test", {}, "test", "test")
