# pylint: disable=redefined-outer-name
"""Tests for transform function """
import json
from service.transforms.submission_transform import SubmissionTransform

def test_bluebeam_adu_files_transform():
    """ test bluebeam_adu_files_transform """
    with open('tests/mocks/submission_data.json', 'r') as file_obj:
        submission_data = json.load(file_obj)
    assert submission_data

    with open('tests/mocks/transform_bluebeam_adu_files.json', 'r') as file_obj:
        transform_data = json.load(file_obj)
    assert transform_data

    transformed = SubmissionTransform.bluebeam_adu_files_transform(submission_data["data"])
    print(transformed)
    assert transformed == transform_data
