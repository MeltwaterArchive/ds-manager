Requirements:
  pip install flask
  
  pip install datasift
  
  git clone https://github.com/mbr/flask-kvsession.git
  
  python ./setup.py install
    
    
To run locally:
  cd into your preferred directory
  
  git clone this to the directory
  
  set up a virtual environment
  
  use pip to install flask and datasift
  
  git clone flask-kvsession to the directory
  
  python console.py
  
  http://127.0.0.1:5000/ds_console
  
  
Quick notes on the new features:
  - (nearly) everything is asynchronous. This minimizes unnecessary API usage, page loading is very fast, and it allows for quick-ish updates on the fly.
  - organization of streams (subscriptions + historics) is a bit different. Historics with push subscriptions are now grouped together for convenience, under 'Historics Streams'. 'Live Streams' are standard push subscriptions only 
  - Multiple stream and Managed Source control: You can look at raw output/log files or stop/start/delete/resume/etc. however many subscriptions, historics, and/or Managed Sources you like with a minimal amount of clicks. 
  - 'Live Stream', 'Usage', and 'Managed Sources' tables are sortable. This is handy to identify problem streams for customers with many, many streams. 'Historics Streams' is not 100% sortable. yet.
  - all raw output and logs are displayed for selected streams, exactly how they would be seen when running curl, and exportable as a text file 
  - 'Live Stream', 'Historics Streams', 'Usage', and 'Managed Sources' can each be individually updated without refreshing the full page.
  - we are using session storage. You'll stay logged in as the last user whose credentials you've last used, unless you clear browser cookies or log out. This also means that you'll only be able to log in as one user per browser (or incognito) as it works currently