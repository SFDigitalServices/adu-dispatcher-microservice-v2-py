"""Welcome submission module"""
#pylint: disable=too-few-public-methods
import os
import sys
import json
import falcon
import jsend
import sentry_sdk
from airtable import Airtable
from .hooks import validate_access
from ..modules.formio import Formio

@falcon.before(validate_access)
class Submission():
    """Submission class"""
    def on_post(self, req, resp):
        #pylint: disable=no-self-use
        """
            on post request
        """
        if req.content_length:
            data = req.stream.read(sys.maxsize)
            data_json = json.loads(data)
            msg = data_json

            with sentry_sdk.configure_scope() as scope:
                scope.set_extra('data_json', data_json)

            if 'id' in data_json:
                # get submission json
                submission_id = data_json['id']
                accela_prj = "" # placeholder accela_prj variable
                accela_sys_id = "" # placeholder accela_sys_id variable

                submission_json = Formio.get_formio_submission_by_id(
                    submission_id, form_id=os.environ.get('FORMIO_FORM_ID_ADU'))
                msg = submission_json

                # init airtable
                airtable = self.get_airtable()
                airtable.insert({
                    'FORMIO_ID': submission_id,
                    'SUBMISSION_DATE':submission_json['created']})
                msg = {'airtable': airtable.get_all()}

                # get record template
                with open('service/templates/accela_submission.json', 'r') as file_obj:
                    template_record = json.load(file_obj)

                if template_record:
                    msg = template_record

                resp.body = json.dumps(jsend.success(msg))
                resp.status = falcon.HTTP_200
                sentry_sdk.capture_message(
                    'ADU Intake {submission_id} {accela_prj} {accela_sys_id}'.format(
                        submission_id=submission_id,
                        accela_prj=accela_prj,
                        accela_sys_id=accela_sys_id
                    ), 'info')
                return

        # catch-all
        resp.status = falcon.HTTP_400
        msg = "The create record information is missing"
        resp.body = json.dumps(jsend.error(msg))
        sentry_sdk.capture_message('ADU Inake Error', 'error')
        return

    @staticmethod
    def get_airtable():
        """ Get airtable """
        return Airtable(
            os.environ.get('AIRTABLE_SUBMISSION_BASE_KEY'),
            os.environ.get('AIRTABLE_SUBMISSION_TABLE_NAME'),
            os.environ.get('AIRTABLE_API_KEY'))
