"""Bluebeam module"""
#pylint: disable=too-few-public-methods
import os
import sys
import json
import logging
import datetime
import falcon
import jsend
import sentry_sdk
import requests
from .dispatch_email import Email
from .hooks import validate_access
from ..modules.util import timer
from ..modules.accela import Accela
from ..modules.common import get_airtable

ERROR_GENERIC = "Bad Request"

#@falcon.before(validate_access)
class DispatchBluebeam():
    """ Bluebeam Dispatch class """

    @staticmethod
    @timer
    def trigger_bluebeam_submission(airtable_record_id):
        """ Trigger Bluebeam Submission """
        url = os.environ.get('DISPATCH_BLUEBEAM_SUBMISSION_URL')
        headers = {
            'ACCESS_KEY': os.environ.get('DISPATCH_BLUEBEAM_SUBMISSION_API_KEY')
        }
        params = {}
        data = json.dumps({
            "airtable_record_id": airtable_record_id
        })
        response = requests.post(url, headers=headers, data=data, params=params)
        response_json = None

        with sentry_sdk.configure_scope() as scope:
            scope.set_extra('trigger_bluebeam_submission_status_code', response.status_code)
            scope.set_extra('trigger_bluebeam_submission_content', response.content)

        if response.status_code == 200:
            response_json = response.json()

        return response_json

    class Submission():

        """ Submission endpoint """
        def on_post(self, req, resp):
            """on post request
            """
            msg = ERROR_GENERIC

            if req.content_length:
                data = req.stream.read(sys.maxsize)
                data_json = json.loads(data)

                try:
                    if 'airtable_record_id' not in data_json:
                        raise ValueError(ERROR_GENERIC)

                    airtable_id = data_json['airtable_record_id']
                    bluebeam_resp = self.dispatch_bluebeam_submission(airtable_id)

                    if bluebeam_resp:
                        resp.body = json.dumps(jsend.success(bluebeam_resp))
                        resp.status = falcon.HTTP_200
                        return

                #pylint: disable=broad-except
                except Exception as exception:
                    logging.exception('DispatchBluebeam.Submission.on_post Exception')
                    if exception.__class__.__name__ == 'ValueError':
                        msg = "{0}".format(exception)
            # catch-all
            resp.status = falcon.HTTP_500
            resp.body = json.dumps(jsend.error(msg))
            sentry_sdk.capture_message('ADU Inake Bluebeam Submission Error', 'error')

        @staticmethod
        def dispatch_bluebeam_submission(airtable_id):
            """ Dispatch Bluebeam submission """
            bluebeam_json = \
                DispatchBluebeam.Submission.get_bluebeam_json_by_airtable_id(airtable_id)

            with sentry_sdk.configure_scope() as scope:
                scope.set_extra('bluebeam_json', bluebeam_json)

            if bluebeam_json:
                bluebeam_resp = DispatchBluebeam.Submission.send_bluebeam_submission(bluebeam_json)
                with sentry_sdk.configure_scope() as scope:
                    scope.set_extra('bluebeam_resp', bluebeam_resp)

                sentry_sdk.capture_message(
                    'ADU Inake Bluebeam Submission '+airtable_id, 'info')

                return bluebeam_resp

            return None

        @staticmethod
        @timer
        def get_bluebeam_json_by_airtable_id(airtable_id):
            """ Get JSON for Bluebeam microservice """
            json_output = None
            # init airtable
            airtable = get_airtable()
            row = airtable.get(airtable_id)
            if row:
                json_output = json.loads(row['fields']['BLUEBEAM_UPLOADS'])

                # attach webhook config
                webhook = {
                    "type": "ADU",
                    "params": {
                        "send_email": 1,
                        "airtable_record_id":airtable_id
                    },
                    "users": []
                }
                email_list = os.environ.get('BLUEBEAM_USER_EMAILS').split(",")
                users = list(map(lambda email: {"email":email}, email_list))
                webhook['users'] = users
                json_output['_webhook'] = webhook

            return json_output

        @staticmethod
        @timer
        def send_bluebeam_submission(bluebeam_json):
            """ Send submission to Bluebeam microservice for processing """
            url = os.environ.get('BLUEBEAM_MS_URL')
            headers = {
                'ACCESS_KEY': os.environ.get('BLUEBEAM_MS_API_KEY')
            }
            params = {}
            data = json.dumps(bluebeam_json)
            response = requests.post(url, headers=headers, data=data, params=params)
            response_json = None

            with sentry_sdk.configure_scope() as scope:
                scope.set_extra('send_bluebeam_submission_status_code', response.status_code)
                scope.set_extra('send_bluebeam_submission_content', response.content)

            if response.status_code == 200:
                response_json = response.json()

            return response_json


    class Webhook():
        """ Webhook endpoint """
        #pylint: disable=no-self-use, line-too-long
        def on_post(self, req, resp):
            """on post request
            """
            msg = ERROR_GENERIC

            if req.content_length:

                data = req.stream.read(sys.maxsize)
                data_json = json.loads(data)

                with sentry_sdk.configure_scope() as scope:
                    scope.set_extra('bb_webhook_json', data_json)

                try:
                    if 'airtable_record_id' not in req.params or \
                        'data' not in data_json or \
                        'bluebeam_project_id' not in data_json['data']:
                        raise ValueError(ERROR_GENERIC)

                    # init airtable
                    airtable = get_airtable()
                    airtable_record_id = req.params['airtable_record_id']
                    bluebeam_json = data_json['data']

                    updated = self.update_submission_airtable_bluebeam(
                        airtable, airtable_record_id, bluebeam_json)

                    with sentry_sdk.configure_scope() as scope:
                        scope.set_extra('bb_updated_json', updated)

                    # Send Email
                    send_email = bool(req.params['send_email']) if 'send_email' in req.params else False
                    if send_email:
                        accela_sys_id = updated['ACCELA_SYS_ID']
                        emails_sent = Email.send_submission_email_by_airtable_id(airtable_record_id)

                        Accela.send_email_to_accela(
                            accela_sys_id, emails_sent['EMAILS'])

                    resp.body = json.dumps(jsend.success(updated))
                    resp.status = falcon.HTTP_200

                    sentry_sdk.capture_message(
                        "ADU Intake Bluebeam uploaded {0} for {1}".format(bluebeam_json['bluebeam_project_id'], airtable_record_id), 'info')

                    return

                #pylint: disable=broad-except
                except Exception as exception:
                    logging.exception('DispatchBlueBeam.Webhook.on_post Exception')
                    if exception.__class__.__name__ == 'ValueError':
                        msg = "{0}".format(exception)

            # catch-all
            resp.status = falcon.HTTP_500
            resp.body = json.dumps(jsend.error(msg))
            sentry_sdk.capture_message('ADU Inake Bluebeam Webhook Error', 'error')

        @staticmethod
        @timer
        def update_submission_airtable_bluebeam(airtable, airtable_id, bluebeam_json):
            """ Update Bluebeam info to submission into Airtable """
            fields = {
                'BLUEBEAM_PRJ_ID': bluebeam_json['bluebeam_project_id'],
                'BLUEBEAM_CREATED_DATE': datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            updated = airtable.update(airtable_id, fields)

            return {
                'ACCELA_PRJ_ID': updated['fields']['ACCELA_PRJ_ID'],
                'ACCELA_SYS_ID': updated['fields']['ACCELA_SYS_ID'],
                'BLUEBEAM_PRJ_ID': updated['fields']['BLUEBEAM_PRJ_ID']
            }
