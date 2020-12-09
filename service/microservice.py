"""Main application module"""
import os
import json
import jsend
import sentry_sdk
import falcon
from .resources.welcome import Welcome
from .resources.submission import Submission
from .resources.dispatch_email import Email
from .resources.dispatch_bluebeam import DispatchBluebeam

def start_service():
    """Start this service
    set SENTRY_DSN environmental variable to enable logging with Sentry
    """
    # Initialize Sentry
    sentry_sdk.init(os.environ.get('SENTRY_DSN'))
    # Initialize Falcon
    api = falcon.API()
    api.add_route('/welcome', Welcome())
    api.add_route('/submission', Submission())
    api.add_route('/email', Email())
    api.add_route('/bluebeam/webhook', DispatchBluebeam().Webhook())
    api.add_route('/bluebeam/submission', DispatchBluebeam().Submission())
    api.add_sink(default_error, '')
    return api

def default_error(_req, resp):
    """Handle default error"""
    resp.status = falcon.HTTP_404
    msg_error = jsend.error('404 - Not Found')

    sentry_sdk.capture_message(msg_error)
    resp.body = json.dumps(msg_error)
