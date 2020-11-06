""" Common functions for tests """
# pylint: disable=unidiomatic-typecheck
def assert_mock(expected, actual):
    """ Assert mock as exected compare to actual response """

    print("asserting type {type} in actual".format(type=type(expected)))
    assert type(expected) == type(actual)

    if expected:
        if isinstance(expected, dict):
            for key, val in expected.items():
                print("asserting {key} in actual".format(key=key))
                assert key in actual
                assert_mock(val, actual[key])
        elif isinstance(expected, list):
            for key, val in enumerate(expected):
                assert_mock(val, actual[key])
        else:
            print("asserting {expected} == {actual}".format(expected=expected, actual=actual))
            assert expected == actual
