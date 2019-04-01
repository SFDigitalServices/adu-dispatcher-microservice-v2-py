# SFDS microservice.py [![CircleCI](https://circleci.com/gh/SFDigitalServices/microservice-py.svg?style=svg)](https://circleci.com/gh/SFDigitalServices/microservice-py)
SFDS microservice.py jumpstarts your next python-based microservice. It consists of a skeleton boilerplate make up of
* [falcon](https://falconframework.org/): bare-metal Python web API framework 
* [gunicorn](https://gunicorn.org/): Python WSGI HTTP Server for UNIX
* [pytest](https://docs.pytest.org/en/latest/): Python testing tool 
* [pylint](https://www.pylint.org/): code analysis for Python
* [sentry](https://sentry.io/): error tracking tool
* [jsend](https://github.com/omniti-labs/jsend):  a specification for a simple, no-frills, JSON based format for application-level communication

## Requirement
* Python3 
([Mac OS X](https://docs.python-guide.org/starting/install3/osx/) / [Windows](https://www.stuartellis.name/articles/python-development-windows/))
* Pipenv & Virtual Environments ([virtualenv](https://docs.python-guide.org/dev/virtualenvs/#virtualenvironments-ref) / [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/))

## Get started

Create your virual environment (e.g. via virtualenvwrapper)
> $ mkvirtualenv microservice-py

Start your virtual environment 
> $ workon microservice-py

Install included packages
> (microservice-py)$ pip install -r requirements.txt

Start WSGI Server
> (microservice-py)$ gunicorn 'service.microservice:start_service()'

Run Pytest
> (microservice-py)$ python -m pytest tests

Get code coverage report
> (microservice-py)$ python -m pytest --cov=service tests/ 

Open with cURL or web browser
> $curl http://127.0.0.1:8000/welcome

## How to fork in own repo (SFDigitalServices use only)
reference: [How to fork your own repo in Github](http://kroltech.com/2014/01/01/quick-tip-how-to-fork-your-own-repo-in-github/)

### Create a new blank repo
First, create a new blank repo that you want to ultimately be a fork of your existing repo. We will call this new repo "my-awesome-microservice-py".

### Clone that new repo on your local machine
Next, make a clone of that new blank repo on your machine:
> $ git clone https://github.com/SFDigitalServices/my-awesome-microservice-py.git

### Add an upstream remote to your original repo
While this technically isn’t forking, its basically the same thing. What you want to do is add a remote upstream to this new empty repo that points to your original repo you want to fork:
> $ git remote add upstream https://github.com/SFDigitalServices/microservice-py.git

### Pull down a copy of the original repo to your new repo
The last step is to pull down a complete copy of the original repo:
> $ git fetch upstream

> $ git merge upstream/master

Or, an easier way:
> $ git pull upstream master

Now, you can work on your new repo to your hearts content. If any changes are made to the original repo, simply execute a `git pull upstream master` and your new repo will receive the updates that were made to the original!

Psst: Don’t forget to upload the fresh copy of your new repo back up to git:

> $ git push origin master




