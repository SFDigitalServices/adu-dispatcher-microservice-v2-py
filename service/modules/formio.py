"""Functions related to interacting with Form.io forms."""
import os
import requests

# pylint: disable=too-few-public-methods
class Formio():
    """Functions related to interacting with Form.io forms."""

    @staticmethod
    def get_formio_submission_by_id(
            submission_id,
            form_id=None,
            base_url=None,
            formio_api_key=None,
        ):
        """Given a query parameters, retreive submissions """

        form_id = form_id if form_id else os.environ.get('FORMIO_FORM_ID')
        base_url = base_url if base_url else os.environ.get('FORMIO_BASE_URL')
        formio_api_key = formio_api_key if formio_api_key else os.environ.get('FORMIO_API_KEY')

        headers = {
            'x-token': '{}'.format(formio_api_key),
            'Content-Type': 'application/json'
        }

        url = '{base_url}/form/{form_id}/submission/{submission_id}'.format(
            base_url=base_url,
            form_id=form_id,
            submission_id=submission_id
        )

        response = requests.get(
            url,
            headers=headers
        )
        response.raise_for_status()

        return response.json()
