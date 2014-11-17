from flask import Flask, render_template,request,session,redirect,url_for
from datasift import Client
from datasift.push import Push
from datasift.request import PartialRequest, DatasiftAuth

app = Flask(__name__)

@app.route('/')
def index():
    return 'heres the index'

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        client = valid_login(request.form['username'], request.form['apikey'])
        if client:
            session['username'] = request.form['username']
            session['apikey'] = request.form['apikey']
            return log_the_user_in()
        else:
            error = 'Invalid username/password'

    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)

def valid_login(user,apikey):
    try:
        client = Client(user,apikey)
        client.balance()
        return client
    except:
        return None

@app.route('/ds_console', methods=['POST', 'GET'])
def log_the_user_in():
    
    error = None 
    name = None
    if request.method == 'POST':
        client = valid_login(request.form['username'], request.form['apikey'])
        if client:
            session['username'] = request.form['username']
            session['apikey'] = request.form['apikey']
            name=session['username']
        else:
            error = 'Invalid username/password'

    # just put responses in strings for now
    pushgetstr = [str(p) for p in push_get_all()]
    historicgetstr = [str(h) for h in historic_get_all()]
    sourcegetstr = [str(s) for s in source_get_all()]

    return render_template(
        'console.html',
        error=error,
        name=name,
        acct=account_all(),
        push=pushgetstr,
        historic=historicgetstr,
        source=sourcegetstr)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('apikey', None)
    return redirect(url_for('log_the_user_in'))

def push_get_all():
    ''' get list of all push subscriptions from API v1.1 '''

    try:
        client = Client(session['username'],session['apikey'])
        per_page = 100

        # custom request, so we can pass all param to API v.1.1 
        #  only for internal accounts?
        request = PartialRequest(
            DatasiftAuth(
                session['username'],
                session['apikey']),
            prefix='push')
        params = {
        'include_finished':1,
        'all':1,
        'order_dir':'desc',
        'per_page':per_page}
        pushget = request.get('get',params)
        pushgetlist = [p for p in pushget['subscriptions']]
        pages = pushget['count']/per_page + 2 

        # >= 2 pages push/get response
        for i in xrange(2,pages):
            params = {
            'include_finished':1,
            'all':1,
            'per_page':per_page,
            'page':i}
            pushget = request.get('get',params)
            pushgetlist.extend([p for p in pushget['subscriptions']])
    except:
        pushgetlist = ["No Push API access"]
    return pushgetlist

def historic_get_all():
    ''' get list of all historics '''
    per_page = 100

    historicgetlist = []
    try:
        client = Client(session['username'],session['apikey'])
        pages = client.historics.get()['count']/per_page + 2
        for i in xrange(1,pages):
            historicget = client.historics.get(maximum=per_page,page=i)
            historicgetlist.extend([h for h in historicget['data']])
    except:
        historicgetlist = ["No Historic API access"]
    return historicgetlist

def source_get_all():
    ''' get list of all managed sources '''
    sourcegetlist = []
    try:
        client = Client(session['username'],session['apikey'])
        per_page = 100

        pages = client.managed_sources.get()['count']/per_page + 2
        for i in xrange(1,pages):
            sourceget = client.managed_sources.get(per_page=per_page,page=i)
            sourcegetlist.extend([s for s in sourceget['sources']])
    except:
        sourcegetlist = ["No Managed Source API access"]
    return sourcegetlist

def account_all():
    ''' get dictionary of usage, balance, and rate limit '''
    try:
        client = Client(session['username'],session['apikey'])
        usage_streams = client.usage(period='day')['streams']
        usage = [ "%s :  %s" % (s,str(usage_streams[s])) for s in usage_streams]
        limit = client.usage().headers['x-ratelimit-limit']
        limit_remaining = client.usage().headers['x-ratelimit-remaining']
        acct = {'balance':str(client.balance()),
        'usage':usage,
        'x-ratelimit-remaining':limit_remaining,
        'x-ratelimit-limit':limit}
    except:
        acct = {'balance':"",
        'usage':"",
        'x-ratelimit-remaining':"",
        'x-ratelimit-limit':""}
    return acct

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.debug = True
    app.run()