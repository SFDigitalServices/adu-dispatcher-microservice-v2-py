"""Welcome submission module"""
#pylint: disable=too-few-public-methods
import os
import sys
import json
import falcon
import jsend
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

            if 'id' in data_json:
                submission_id = data_json['id']
                submission_json = Formio.get_formio_submission_by_id(
                    submission_id, form_id=os.environ.get('FORMIO_FORM_ID_ADU'))
                msg = submission_json

                resp.body = json.dumps(jsend.success(msg))
                resp.status = falcon.HTTP_200
                return

        # catch-all
        resp.status = falcon.HTTP_400
        msg = "The create record information is missing"
        resp.body = json.dumps(jsend.error(msg))
        return
