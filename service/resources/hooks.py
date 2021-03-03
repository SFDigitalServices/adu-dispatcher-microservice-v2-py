""" hooks """
import os
import falcon

def validate_access(req, _resp, _resource, _params):
    """ validate access method """
    access_key = os.environ.get('ACCESS_KEY')
    if not access_key or \
        (
                req.get_header('ACCESS_KEY') != access_key and
                not (req.host == '127.0.0.1' and req.get_header('x-apikey') == access_key)
        ):
        raise falcon.HTTPForbidden(description='Access Denied')
