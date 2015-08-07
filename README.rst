Requirements:
  Local environment: 
    Python 2.7
    virtualenv
    pip
  Dependencies:
    use requirements.txt with pip to get all dependencies
    
To run locally:
  1. cd into your preferred directory
  2. git clone this to the directory
  3. set up a local virtual environment: 
    a. pip install virtualenv
    b. virtualenv venv
    c. source venv/bin/activate
  4. install dependencies: pip install -r requirements.txt
  5. run from terminal: python application.py
  6. from browser: navigate to http://127.0.0.1:5000/
  
Note on elasticbeanstalk use:
  - application.py has just a single import which makes it a WSGI application. Otherwise eb complains "Target WSGI script '/opt/python/current/app/application.py' does not contain WSGI application 'application'"
  - make sure that Configuration is using something like "64bit Amazon Linux 2015.03 v1.4.3 running Python 2.7" (note Python version)
  
==== RELEASE NOTES ====

2015-08-07

  - elastic beanstalk support 
  - new PYLON recordings section for all identities
  - start/stop PYLON recordings from any identity
  - improved output in the case that there's no data in a section 

2015-07-09:

  - renamed to DS Manager
  - new ACCOUNT Identities section: include new endpoints for Account identities 
  - updated to be used with elasticbeanstalk
  - add DPU calculations
  - historics fixes incl. multiple push subscriptions
  - prettier style and formatting incl. section tables and raw output display
  - better README format

2015-01-27:

  - (nearly) everything is asynchronous. This minimizes unnecessary API usage, page loading is very fast, and it allows for quick-ish updates on the fly.
  - organization of streams (subscriptions + historics) is a bit different. Historics with push subscriptions are now grouped together for convenience, under 'Historics Streams'. 'Live Streams' are standard push subscriptions only 
  - Multiple stream and Managed Source control: You can look at raw output/log files or stop/start/delete/resume/etc. however many subscriptions, historics, and/or Managed Sources you like with a minimal amount of clicks. 
  - 'Live Stream', 'Usage', and 'Managed Sources' tables are sortable. This is handy to identify problem streams for customers with many, many streams. 'Historics Streams' is not 100% sortable. yet.
  - all raw output and logs are displayed for selected streams, exactly how they would be seen when running curl, and exportable as a text file 
  - 'Live Stream', 'Historics Streams', 'Usage', and 'Managed Sources' can each be individually updated without refreshing the full page.
  - we are using session storage. You'll stay logged in as the last user whose credentials you've last used, unless you clear browser cookies or log out. This also means that you'll only be able to log in as one user per browser (or incognito) as it works currently
