""" TransformBase module """
#pylint: disable=too-few-public-methods,no-self-use
import re

class TransformBase():
    """ Base module for Transforms """

    def transform(self, data):
        """
        abstract transform function
        given input, does some transformation and return output
        """
        output = data
        return output

    @staticmethod
    def pretty_string(name):
        """ Change name from camelCase to words """
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', name).title()
