"""Submission module"""
#pylint: disable=too-few-public-methods
import os
import sys
import json
import datetime
import threading
import falcon
import jsend
import sentry_sdk
from .dispatch_email import Email
from .dispatch_bluebeam import DispatchBluebeam
from .hooks import validate_access
from ..modules.util import timer
from ..modules.accela import Accela
from ..modules.formio import Formio
from ..modules.common import get_airtable, has_option_req
from ..transforms.submission_transform import SubmissionTransform



@falcon.before(validate_access)
class Submission():
    """Submission class"""
    def on_post(self, req, resp):
        #pylint: disable=no-self-use,too-many-locals,too-many-statements
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

                enable_bluebeam = has_option_req(req, 'BLUEBEAM')
                send_email = has_option_req(req, 'EMAIL')

                with sentry_sdk.configure_scope() as scope:
                    scope.set_extra('enable_bluebeam', enable_bluebeam)
                    scope.set_extra('send_email', send_email)

                submission_json = self.get_submssion_json(submission_id)

                # init airtable
                airtable = get_airtable()
                # log submission
                insert = self.create_submission_airtable(airtable, submission_id, submission_json)
                airtable_id = insert["id"]

                # transform submission into record
                record_json = SubmissionTransform().accela_transform(submission_json)

                # send record to accela
                response = Accela.send_record_to_accela(record_json)

                with sentry_sdk.configure_scope() as scope:
                    scope.set_extra('accela_resp_status_code', response.status_code)
                    scope.set_extra('accela_resp_json', response.json())

                if response.status_code == 200:
                    accela_json = response.json()

                    accela_prj_id = accela_json['result']['customId']
                    accela_sys_id = accela_json['result']['id']

                    self.update_submission_airtable(airtable, airtable_id, accela_json)

                    #pylint: disable=line-too-long
                    sentry_sdk.capture_message(
                        'ADU Intake {submission_id} {accela_env} {accela_prj_id} {accela_sys_id}'.format(
                            submission_id=submission_id,
                            accela_prj_id=accela_prj_id,
                            accela_sys_id=accela_sys_id,
                            accela_env=os.environ.get('ACCELA_ENV')
                        ), 'info')

                    if enable_bluebeam:
                        accela_json['airtable'] = {"id": airtable_id}

                        # threading bluebeam submission
                        thread = threading.Thread(target=DispatchBluebeam.trigger_bluebeam_submission, args=(airtable_id, send_email))
                        thread.start()

                    else:
                        if send_email:
                            emails_sent = Email.send_submission_email_by_airtable_id(airtable_id)

                            response_emails = Accela.send_email_to_accela(
                                accela_json['result']['id'], emails_sent['EMAILS'])

                            accela_json['emails'] = response_emails.json()

                    msg = accela_json

                    resp.body = json.dumps(jsend.success(msg))
                    resp.status = falcon.HTTP_200

                    with sentry_sdk.configure_scope() as scope:
                        scope.set_extra('msg_json', msg)

                    #pylint: disable=line-too-long
                    sentry_sdk.capture_message(
                        'ADU Intake Success {submission_id} {accela_env} {accela_prj_id} {accela_sys_id}'.format(
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
            'NUM_PROPOSED_ADU': len(submission_json['data']['proposedAdUs']),
            'BLUEBEAM_UPLOADS': json.dumps(
                SubmissionTransform().bluebeam_transform(submission_json)
                ),
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
