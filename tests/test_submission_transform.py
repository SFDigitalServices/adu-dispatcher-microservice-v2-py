# pylint: disable=redefined-outer-name
"""Tests for submission_transform function """
import json
from service.transforms.transform import TransformBase
from service.transforms.submission_transform import SubmissionTransform

def test_transform_base():
    """ test transform_base """
    txt = "HelloWorld"
    assert txt == TransformBase().transform(txt)

    assert TransformBase.pretty_string(txt) == "Hello World"

def test_submission_template(monkeypatch):
    """ test submission populate_template """
    monkeypatch.setenv("UPLOAD_HOST", "https://localhost")

    with open('service/templates/accela_submission.json', 'r') as file_obj:
        template_record = json.load(file_obj)
    assert template_record

    with open('tests/mocks/submission_data.json', 'r') as file_obj:
        submission_data = json.load(file_obj)
    assert submission_data

    with open('tests/mocks/submission_accela_transformed.json', 'r') as file_obj:
        submission_transformed = json.load(file_obj)
    assert submission_transformed

    output = SubmissionTransform().populate_template(template_record, submission_data)
    assert submission_transformed == output

    # test submission variant for New Construction
    submission_data['data']['whereProposedAduLocated'] = "newConstruction"
    for idx, form in enumerate(submission_transformed['customForms']):
        if form['id'] == "PLN_PRJ-PROJECT.cDESCRIPTION":
            submission_transformed['customForms'][idx]['Additions'] = ""
            submission_transformed['customForms'][idx]['New Construction'] = "CHECKED"

    with open('service/templates/accela_submission.json', 'r') as file_obj:
        template_record = json.load(file_obj)
    assert template_record

    output = SubmissionTransform().populate_template(template_record, submission_data)
    assert submission_transformed == output
