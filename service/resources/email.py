"""Welcome example module"""
#pylint: disable=too-few-public-methods
import sys
import os
import json
import logging
import datetime
import pytz
import falcon
import sentry_sdk
import jsend
from ..modules.common import get_airtable,email

ERROR_GENERIC = "Bad Request"
ERROR_401 = "Unauthorized"

class Email():
    """Email class"""
    def on_post(self, req, resp):
        #pylint: disable=no-self-use
        """on post request
        """
        msg = ERROR_GENERIC

        if req.content_length:
            data = req.stream.read(sys.maxsize)
            data_json = json.loads(data)

            try:
                #pylint: disable=line-too-long
                if 'airtable_record_id' not in data_json or data_json['token'] != os.environ.get('EMAIL_TOKEN'):
                    raise ValueError(ERROR_401)

                # init airtable
                airtable_id = data_json['airtable_record_id']
                airtable = get_airtable()

                row = airtable.get(airtable_id)

                msg = {'airtable': row}

                prj_number = row['fields']['ACCELA_PRJ_ID']
                #staff_sub = self.get_staff_email_substitutions(prj_number, row['fields']['PROJECT_ADDRESS'], row['fields']['SUBMISSION_DATE'])
                # applicant_sub = self.get_applicant_email_substitutions(prj_number,
                # row['fields']['PROJECT_ADDRESS'],
                # row['fields']['FIRST_NAME']+ ' ' +row['fields']['LAST_NAME'],
                # row['fields']['ACCELA_SYS_ID'])
                # msg = self.get_email_text('email_applicant', applicant_sub)
                # print(msg)

                self.email_applicant(row['fields']['EMAIL'],
                    prj_number,
                    row['fields']['PROJECT_ADDRESS'],
                    row['fields']['FIRST_NAME']+ ' ' +row['fields']['LAST_NAME'],
                    row['fields']['ACCELA_SYS_ID'])
                self.email_staff(prj_number, row['fields']['PROJECT_ADDRESS'], row['fields']['SUBMISSION_DATE'])

                resp.body = json.dumps(jsend.success(msg))
                resp.status = falcon.HTTP_200

                sentry_sdk.capture_message('ADU Inake Email Sent '+prj_number, 'info')
                return
            #pylint: disable=broad-except
            except Exception as exception:
                logging.exception('Email.on_post Exception')
                if exception.__class__.__name__ == 'ValueError':
                    msg = "{0}".format(exception)

        # catch-all
        resp.status = falcon.HTTP_500
        resp.body = json.dumps(jsend.error(msg))
        sentry_sdk.capture_message('ADU Inake Email Error', 'error')

    @staticmethod
    def get_email_text(template, substitutions):
        """ get email text content """
        with open('service/templates/'+template+'.txt', 'r') as file_obj:
            text_content = file_obj.read()
        for key in substitutions:
            text_content = text_content.replace(key, substitutions[key])
        return text_content

    @staticmethod
    def email_staff(prj_number, project_address, submission_date_iso):
        """ Staff email """
        substitutions = Email.get_staff_email_substitutions(
            prj_number, project_address, submission_date_iso)
        with open('service/templates/email_staff.html', 'r') as file_obj:
            html_template = file_obj.read()

        with open('service/templates/email_staff.txt', 'r') as file_obj:
            text_template = file_obj.read()

        subject = "New Application for ADU at {project_address}".format(
            project_address=project_address)

        email(os.environ.get('EMAIL_STAFF'), subject, substitutions, html_template, text_template)

    @staticmethod
    def get_staff_email_substitutions(prj_number, project_address, submission_date_iso):
        """ get email substitution for staff """
        timezone = pytz.timezone('America/Los_Angeles')
        #pylint: disable=line-too-long
        submission_date_obj = datetime.datetime.fromisoformat(submission_date_iso[:-1]).replace(tzinfo=pytz.utc)
        submission_date = submission_date_obj.astimezone(timezone).strftime('%Y-%m-%d %I:%M %p')
        substitutions = {
                '-prj_number-': prj_number,
                '-proj_address-': project_address,
                '-submission_date-': submission_date
        }
        return substitutions

    @staticmethod
    #pylint: disable=line-too-long
    def get_applicant_email_substitutions(prj_number, project_address, applicant_name, accela_sys_id):
        """ get email substitution for applicant """
        accela_sys_caps = accela_sys_id.split('-')
        accela_link = "{accela_url}&capID1={cap1}&capID2={cap2}&capID3={cap3}".format(
            accela_url=os.environ.get('ACCELA_URL'),
            cap1=accela_sys_caps[1],
            cap2=accela_sys_caps[2],
            cap3=accela_sys_caps[3],
        )
        substitutions = {
                '-applicant_name-': applicant_name,
                '-prj_number-': prj_number,
                '-proj_address-': project_address,
                '-accela_link-': accela_link,

        }
        return substitutions

    @staticmethod
    #pylint: disable=line-too-long
    def email_applicant(applicant_email, prj_number, project_address, applicant_name, accela_sys_id):
        """ Applicant email """
        substitutions = Email.get_applicant_email_substitutions(
            prj_number, project_address, applicant_name, accela_sys_id)
        with open('service/templates/email_applicant.html', 'r') as file_obj:
            html_template = file_obj.read()

        with open('service/templates/email_applicant.txt', 'r') as file_obj:
            text_template = file_obj.read()

        subject = "You submitted your ADU application for {project_address}".format(
            project_address=project_address)

        email(applicant_email, subject, substitutions, html_template, text_template)
