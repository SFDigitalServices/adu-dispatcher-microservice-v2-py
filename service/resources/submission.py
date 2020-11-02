"""Welcome submission module"""
#pylint: disable=too-few-public-methods
import os
import sys
import json
import datetime
import falcon
import jsend
import sentry_sdk
import requests
from .dispatch_email import Email
from .hooks import validate_access
from ..modules.util import timer
from ..modules.formio import Formio
from ..modules.common import get_airtable
from ..transforms.submission_transform import SubmissionTransform



@falcon.before(validate_access)
class Submission():
    """Submission class"""
    def on_post(self, req, resp):
        #pylint: disable=no-self-use,too-many-locals
        """
            on post request
        """
        if req.content_length:
            data = req.stream.read(sys.maxsize)
            data_json = json.loads(data)

            with sentry_sdk.configure_scope() as scope:
                scope.set_extra('data_json', data_json)

            if 'id' in data_json:
                # get submission json
                submission_id = data_json['id']
                accela_prj_id = "" # placeholder accela_prj variable
                accela_sys_id = "" # placeholder accela_sys_id variable

                submission_json = self.get_submssion_json(submission_id)

                # init airtable
                airtable = get_airtable()
                # log submission
                insert = self.create_submission_airtable(airtable, submission_id, submission_json)
                airtable_id = insert["id"]

                # transform submission into record
                record_json = SubmissionTransform().transform(submission_json)

                # send record to accela
                response = self.send_record_to_accela(record_json)

                if response.status_code == 200:
                    content_json = response.json()

                    self.update_submission_airtable(airtable, airtable_id, content_json)

                    emails_sent = Email.send_submission_email_by_airtable_id(airtable_id)

                    response_emails = self.send_email_to_accela(
                        content_json['result']['id'], emails_sent['EMAILS'])

                    with sentry_sdk.configure_scope() as scope:
                        scope.set_extra('accela_re_emails_status_code', response_emails.status_code)
                        scope.set_extra('accela_re_emails_json', response_emails.json())

                    content_json['result']['emails'] = response_emails.json()
                    msg = content_json

                    resp.body = json.dumps(jsend.success(msg))
                    resp.status = falcon.HTTP_200
                    #pylint: disable=line-too-long
                    sentry_sdk.capture_message(
                        'ADU Intake {submission_id} {accela_env} {accela_prj_id} {accela_sys_id}'.format(
                            submission_id=submission_id,
                            accela_prj_id=accela_prj_id,
                            accela_sys_id=accela_sys_id,
                            accela_env=os.environ.get('ACCELA_ENV')
                        ), 'info')
                    return

                with sentry_sdk.configure_scope() as scope:
                    scope.set_extra('accela_response_status_code', response.status_code)
                    scope.set_extra('accela_response_json', response.json())


        # catch-all
        resp.status = falcon.HTTP_400
        msg = "The create record information is missing"
        resp.body = json.dumps(jsend.error(msg))
        sentry_sdk.capture_message('ADU Inake Error', 'error')
        return

    @staticmethod
    @timer
    def create_submission_airtable(airtable, submission_id, submission_json):
        """ Create submission into AirTable """
        return airtable.insert({
            'FORMIO_ID': submission_id,
            'SUBMISSION_DATE': submission_json['created'],
            'PROJECT_ADDRESS': submission_json['data']['projectAddress'],
            'FIRST_NAME': submission_json['data']['firstName'],
            'LAST_NAME': submission_json['data']['lastName'],
            'EMAIL': submission_json['data']['email'],
            'ACCELA_ENV': os.environ.get('ACCELA_ENV')
        })

    @staticmethod
    @timer
    def update_submission_airtable(airtable, airtable_id, accela_json):
        """ Update submission into Airtable """
        fields = {
            'ACCELA_PRJ_ID': accela_json['result']['customId'],
            'ACCELA_SYS_ID': accela_json['result']['id'],
            'ACCELA_CREATED_DATE': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        update = airtable.update(airtable_id, fields)
        return update

    @staticmethod
    @timer
    def get_submssion_json(submission_id):
        """ Get Submission JSON """
        submission_json = Formio.get_formio_submission_by_id(
            submission_id, form_id=os.environ.get('FORMIO_FORM_ID_ADU'))
        return submission_json

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
        return response
