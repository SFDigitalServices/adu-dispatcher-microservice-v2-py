""" Common functions """
import os
from airtable import Airtable
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, From
from ..modules.util import timer

@timer
def get_airtable():
    """ Get airtable """
    return Airtable(
        os.environ.get('AIRTABLE_SUBMISSION_BASE_KEY'),
        os.environ.get('AIRTABLE_SUBMISSION_TABLE_NAME'),
        os.environ.get('AIRTABLE_API_KEY'))

@timer
def email(email_to, subject, substitutions, html_content, text_content):
    """ Send email """
    from_email = From(email=os.environ.get('EMAIL_FROM'), name=os.environ.get('EMAIL_FROM_NAME'))

    # create our To list to pass to our mail object
    # the substitutions in this list are the dynamic HTML values
    to_email = To(
        email=email_to,
        substitutions=substitutions
    )

    # create our Mail object and populate dynamically with our to_emails
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
        plain_text_content=text_content,
        is_multiple=True)

    # create our sendgrid client object, pass it our key, then send and return our response objects
    try:
        sendgrid = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print(f"Response code: {code}")
        print(f"Response headers: {headers}")
        print(f"Response body: {body}")
        print("HTML Messages Sent!")
    #pylint: disable=broad-except
    except Exception as ex:
        print("Error: {0}".format(ex))
    return str(response.status_code)

def get_accela_link_by_id(accela_sys_id):
    """ Get accela link by Accela system id """
    accela_sys_caps = accela_sys_id.split('-')
    accela_link = "{accela_url}&capID1={cap1}&capID2={cap2}&capID3={cap3}".format(
        accela_url=os.environ.get('ACCELA_URL'),
        cap1=accela_sys_caps[1],
        cap2=accela_sys_caps[2],
        cap3=accela_sys_caps[3],
    )
    return accela_link
