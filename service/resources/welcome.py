"""Welcome example module"""
import json
import falcon
import jsend

class Welcome():
    """Welcome class"""
    def on_get(self, _req, resp):
        """on get request
        return Welcome message
        """
        msg = {'message': 'Welcome'}
        resp.body = json.dumps(jsend.success(msg))
        resp.status = falcon.HTTP_200
