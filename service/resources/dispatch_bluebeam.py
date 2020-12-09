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
from ..modules.formio import Formio
from ..modules.common import get_airtable
from ..transforms.submission_transform import SubmissionTransform

ERROR_GENERIC = "Bad Request"

#@falcon.before(validate_access)
class DispatchBluebeam():
    """ Bluebeam Dispatch class """
    class Submission():
        """ Submission endpoint """
        pass

    class Webhook():
        """ Webhook endpoint """
        #pylint: disable=no-self-use, line-too-long
        def on_post(self, req, resp):
            """on post request
        """
            msg = ERROR_GENERIC

            if 'airtable_record_id' in req.params and req.content_length:
                airtable_record_id = req.params['airtable_record_id']
                data = req.stream.read(sys.maxsize)
                data_json = json.loads(data)

                with sentry_sdk.configure_scope() as scope:
                    scope.set_extra('bb_webhook_json', data_json)

                try:
                    if 'data' not in data_json or 'bluebeam_project_id' not in data_json['data']:
                        raise ValueError(ERROR_GENERIC)

                    # init airtable
                    airtable = get_airtable()
                    bluebeam_json = data_json['data']
                    bluebeam_prj_id = bluebeam_json['bluebeam_project_id']
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
                        'ADU Inake Bluebeam uploaded '+bluebeam_prj_id, 'info')

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
