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
    if request.method == 'POST':
        client = valid_login(request.form['username'], request.form['apikey'])
        if isinstance(client, dict):
            error = client['error']
        elif client:
            #clear old session data 
            pop_session()
            session['username'] = request.form['username']
            session['apikey'] = request.form['apikey']
            name=session['username']
        else:
            error = 'Invalid username/password'
    else:
        if 'username' in session.keys():
            name=session['username']

    return render_template(
        'manager.html',
        error=error,
        name=name,
        acct=account_all())


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    pop_session()
    return redirect(url_for('manager'))

@app.route('/reset_usage')
def reset_usage():
    if 'usage' in session.keys():
        session.pop('usage', None)
    response = make_response("",204)
    return response

@app.route('/reset_account')
def reset_account():
    if 'identities' in session.keys():
        session.pop('identities', None)
    response = make_response("",204)
    return response

@app.route('/reset_pylon')
def reset_pylon():
    if 'pylon' in session.keys():
        session.pop('pylon', None)
    response = make_response("",204)
    return response

@app.route('/reset_push')
def reset_push():
    if 'push' in session.keys():
        session.pop('push', None)
    response = make_response("",204)
    return response

@app.route('/reset_historics')
def reset_historics():
    if 'historics' in session.keys():
        session.pop('historics', None)
    response = make_response("",204)
    return response

@app.route('/reset_sources')
def reset_sources():
    if 'sources' in session.keys():
        session.pop('sources', None)
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
        balance = client.balance()
        session['ratelimit'] = balance.headers['x-ratelimit-remaining']
        return client
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
        usage = client.usage(period='day')
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