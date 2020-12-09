"""Functions related to interacting with Accela."""
import os
import json
import requests
import sentry_sdk
from ..modules.util import timer

# pylint: disable=too-few-public-methods
class Accela():
    """Functions related to interacting with Accela."""

    @staticmethod
    @timer
    def send_email_to_accela(record_id, emails):
        """ Send record to Accela """
        url = os.environ.get('ACCELA_MS_BASE_URL') + '/records/' + record_id + '/comments'
        headers = {
            'X-SFDS-APIKEY': os.environ.get('ACCELA_MS_APIKEY'),
            'X-ACCELA-ENV': os.environ.get('ACCELA_ENV'),
            'X-ACCELA-USERNAME': os.environ.get('ACCELA_USERNAME')
        }
        params = {}
        data = json.dumps(emails)
        response = requests.put(url, headers=headers, data=data, params=params)

        with sentry_sdk.configure_scope() as scope:
            scope.set_extra('accela_re_emails_status_code', response.status_code)
            scope.set_extra('accela_re_emails_json', response.json())

        return response

    @staticmethod
    @timer
    def send_record_to_accela(record_json):
        """ Send record to Accela """
        url = os.environ.get('ACCELA_MS_BASE_URL') + '/records'
        headers = {
            'X-SFDS-APIKEY': os.environ.get('ACCELA_MS_APIKEY'),
            'X-ACCELA-ENV': os.environ.get('ACCELA_ENV'),
            'X-ACCELA-USERNAME': os.environ.get('ACCELA_USERNAME')
        }
        params = {}
        data = json.dumps(record_json)
        response = requests.post(url, headers=headers, data=data, params=params)

        return response
