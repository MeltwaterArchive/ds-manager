from flask import Flask, render_template,request,session,redirect,url_for,jsonify,make_response
from datasift import Client
from views import usage,account,pylon,source,push,historics
from flask_kvsession import KVSessionExtension
from simplekv.fs import FilesystemStore
import datetime,os,sys,logging

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

data_directory = "./data"
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# use local filesystem for session storage instead of default client sessions
store = FilesystemStore(data_directory)
KVSessionExtension(store, app)

# register blueprints 
app.register_blueprint(usage.usage, url_prefix='/usage')
app.register_blueprint(account.account, url_prefix='/account')
app.register_blueprint(pylon.pylon, url_prefix='/pylon')
app.register_blueprint(source.source, url_prefix='/source')
app.register_blueprint(push.push, url_prefix='/push')
app.register_blueprint(historics.historics, url_prefix='/historics')

@app.route('/')
def index():
    return redirect(url_for('manager'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        client = valid_login(request.form['username'], request.form['apikey'])
        if client:
            session['username'] = request.form['username']
            session['apikey'] = request.form['apikey']
            return manager()
        else:
            error = 'Invalid username/password'

    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)


@app.route('/ds_console')
def ds_console():
    # redirect from old endpoint
    return redirect(url_for('manager'))

@app.route('/manager', methods=['POST', 'GET'])
def manager():
    
    # login dialog, set session stuff
    error = None 
    name = None
    acct = None
    if request.method == 'POST':
        client = valid_login(request.form['username'], request.form['apikey'])
        if isinstance(client, dict):
            error = client['error']
        elif isinstance(client,basestring):
            error = client
        elif client:
            #clear old session data, then repopulate and get account data
            pop_session()
            session['username'] = request.form['username']
            session['apikey'] = request.form['apikey']
            name=session['username']
            acct=account_all()
        else:
            error = "something's wrong"

    else:
        if 'username' in session.keys():
            name=session['username']

    return render_template(
        'manager.html',
        error=error,
        name=name,
        acct=acct)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    pop_session()
    return redirect(url_for('manager'))

# reset pretty much all session data except user and api key on page refresh
@app.route('/reset_data')
def reset_data():
    session_keys = ["usage","identities","pylon","push","historics","sources"]
    for k in session_keys: 
        if k in session.keys():
            session.pop(k, None)
    response = make_response("",204)
    return response


@app.route('/update_ratelimit')
def update_ratelimit():
    if 'ratelimit' in session.keys():
        response = make_response(session['ratelimit'],200)
    else:
        response = make_response("",200)
    return response




'''
HELPER FUNCTIONS
'''

def valid_login(user,apikey):
    try:
        client = Client(user,apikey)
        usage = client.usage(period='day')

        # make sure that we're using account credentials, not idenitity 
        if usage:
            session['usage'] = usage
            session['ratelimit'] = usage.headers['x-ratelimit-remaining']
            return client
        else:
            return "Use an account API key"
    except Exception, e:
        return e.message

def pop_session():
    for k in session.keys():
        session.pop(k, None)


# general account details.. (not identities)
def account_all():
    ''' get dictionary of usage, balance, and rate limit '''
    try:
        client = Client(session['username'],session['apikey'])
        if not session['usage']:
         session['usage']=client.usage(period='day')
        # transform usage response as a list of tuples
        usage_streams = usage['streams'].items()
        usage_period = (usage['start'],usage['end'])
        limit = (usage.headers['x-ratelimit-remaining'], usage.headers['x-ratelimit-limit'])
        session['ratelimit'] = usage.headers['x-ratelimit-remaining']
        acct = {'balance':client.balance(),
        'usage_streams':usage_streams,
        'usage_period': usage_period,
        'limit':limit}
    except:
        acct = {'balance':"",
        'usage':"",
        'x-ratelimit-remaining':"",
        'x-ratelimit-limit':""}
    return acct

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.debug = True
    app.threaded = True
    app.run()