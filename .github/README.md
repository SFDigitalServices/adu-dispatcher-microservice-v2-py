# SFDS ADU Dispatcher v2 [![CircleCI](https://badgen.net/circleci/github/SFDigitalServices/adu-dispatcher-microservice-v2-py/main)](https://circleci.com/gh/SFDigitalServices/adu-dispatcher-microservice-v2-py) [![Coverage Status](https://coveralls.io/repos/github/SFDigitalServices/adu-dispatcher-microservice-v2-py/badge.svg?branch=main)](https://coveralls.io/github/SFDigitalServices/adu-dispatcher-microservice-v2-py?branch=main)
SFDS ADU Dispatcher v2 is the second iteration of the SFDS ADU Dispatcher to support renewed effort to digitalize accessory dwelling unit (ADU) permitting. 

## Dispatcher endpoints

### Create new submission
This endpoint takes in a form submission ID and completes the process to push the submission data into Accela via [Accela Microservice](https://github.com/SFDigitalServices/accela-microservice-py). Upon successful submission, email notifications will be sent out to the applicant and staff with Accela PRJ and web link to track the application. 

This transaction will also log meta data in an Airtable for tracking.
```
curl --location --request POST '<ADU_DISPATCHER_HOST>/submission' \
--header 'ACCESS_KEY: XXXXXXXX' \
--header 'Content-Type: application/json' \
--data-raw '{
    "id": "<FORM_SUBMISSION_ID>"
}'
```

### Resend email notifications
This endpoint takes in an airtable record ID and resends confirmations to applicant and staff.  

This transaction will also be logged within Accela in the PRJ record under Internal Notes section. 
```
curl --location --request POST '<ADU_DISPATCHER_HOST>/email' \
--header 'Content-Type: application/json' \
--data-raw '{
    "token": "<EMAIL_TOKEN>",
    "airtable_record_id": "<AIRTABLE_RECORD_ID>"
}'
```

## Built with SFDS microservice.py framework
[SFDS microservice.py](https://github.com/SFDigitalServices/microservice-py) framework jumpstarts your next python-based microservice. It consists of a skeleton boilerplate make up of
* [falcon](https://falconframework.org/): bare-metal Python web API framework 
* [gunicorn](https://gunicorn.org/): Python WSGI HTTP Server for UNIX
* [pytest](https://docs.pytest.org/en/latest/): Python testing tool 
* [pylint](https://www.pylint.org/): code analysis for Python
* [sentry](https://sentry.io/): error tracking tool
* [jsend](https://github.com/omniti-labs/jsend):  a specification for a simple, no-frills, JSON based format for application-level communication

### Requirement
* Python3 
([Mac OS X](https://docs.python-guide.org/starting/install3/osx/) / [Windows](https://www.stuartellis.name/articles/python-development-windows/))
* Pipenv & Virtual Environments ([virtualenv](https://docs.python-guide.org/dev/virtualenvs/#virtualenvironments-ref) / [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/))

### Get started

Install Pipenv (if needed)
> $ pip install --user pipenv

Install included packages
> $ pipenv install

Set ACCESS_KEY environment var and start WSGI Server
> $ ACCESS_KEY=123456 pipenv run gunicorn 'service.microservice:start_service()'

Run Pytest
> $ pipenv run python -m pytest

Get code coverage report
> $ pipenv run python -m pytest --cov=service tests/ --cov-fail-under=100

Open with cURL or web browser
> $ curl --header "ACCESS_KEY: 123456" http://127.0.0.1:8000/welcome

### How to fork in own repo (SFDigitalServices use only)
reference: [How to fork your own repo in Github](http://kroltech.com/2014/01/01/quick-tip-how-to-fork-your-own-repo-in-github/)

#### Create a new blank repo
First, create a new blank repo that you want to ultimately be a fork of your existing repo. We will call this new repo "my-awesome-microservice-py".

#### Clone that new repo on your local machine
Next, make a clone of that new blank repo on your machine:
> $ git clone https://github.com/SFDigitalServices/my-awesome-microservice-py.git

#### Add an upstream remote to your original repo
While this technically isn’t forking, its basically the same thing. What you want to do is add a remote upstream to this new empty repo that points to your original repo you want to fork:
> $ git remote add upstream https://github.com/SFDigitalServices/microservice-py.git

#### Pull down a copy of the original repo to your new repo
The last step is to pull down a complete copy of the original repo:
> $ git fetch upstream

> $ git merge upstream/main

Or, an easier way:
> $ git pull upstream main

Now, you can work on your new repo to your hearts content. If any changes are made to the original repo, simply execute a `git pull upstream main` and your new repo will receive the updates that were made to the original!

Psst: Don’t forget to upload the fresh copy of your new repo back up to git:

> $ git push origin main

### Development 
Auto-reload on code changes
> $ pipenv run gunicorn --bind=127.0.0.1:8001 --reload 'service.microservice:start_service()'

Code coverage command with missing statement line numbers  
> $ pipenv run python -m pytest --cov=service tests/ --cov-report term-missing

Set up git hook scripts with pre-commit
> $ pipenv run pre-commit install


## Continuous integration
* CircleCI builds fail when trying to run coveralls.
    1. Log into coveralls.io to obtain the coverall token for your repo.
    2. Create an environment variable in CircleCI with the name COVERALLS_REPO_TOKEN and the coverall token value.

## Heroku Integration
* Set ACCESS_TOKEN environment variable and pass it as a header in requests
