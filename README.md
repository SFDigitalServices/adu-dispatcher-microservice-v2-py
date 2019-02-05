# SFDS middleware.py
SFDS middleware.py jumpstarts your next python-based middleware microservice. It consists of a skeleton boilerplate make up of
* [falcon](https://falconframework.org/): bare-metal Python web API framework 
* [gunicorn](https://gunicorn.org/): Python WSGI HTTP Server for UNIX
* [pytest](https://docs.pytest.org/en/latest/): Python testing tool 
* [sentry](https://sentry.io/): error tracking tool
* [jsend](https://github.com/omniti-labs/jsend):  a specification for a simple, no-frills, JSON based format for application-level communication

## Requirement
* Python3 
([Mac OS X](https://docs.python-guide.org/starting/install3/osx/) / [Windows](https://www.stuartellis.name/articles/python-development-windows/))
* Pipenv & Virtual Environments ([virtualenv](https://docs.python-guide.org/dev/virtualenvs/#virtualenvironments-ref) / [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/))

## Get started

Create your virual environment (e.g. via virtualenvwrapper)
> $ mkvirtualenv sfds-mwpy

Start your virtual environment 
> $ workon sfds-mwpy

Install included packages
> (sfds-mwpy)$ pip install -r requirements.txt

Start WSGI Server
> (sfds-mwpy)$ gunicorn 'service.middleware:start_service()'

Run Pytest
> (sfds-mwpy)$ pytest tests

Open with cURL or web browser
> $curl http://127.0.0.1:8000/welcome



