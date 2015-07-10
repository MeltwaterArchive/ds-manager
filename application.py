'''
elasticbeanstalk needs the flask app to be called application for whatever reason. 
Default config looks for application.py in the root dir. hence this file.
TODO - virtualenv is always encouraged. Add that in here? https://forums.openshift.com/solved-python-flask-error-cant-find-application
'''
from manager import app as application