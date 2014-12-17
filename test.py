from flask import Flask, render_template,request,session,redirect,url_for,jsonify
from datasift import Client
from datasift.push import Push
from datasift.request import PartialRequest, DatasiftAuth

app = Flask(__name__)

push_get_no_historics = []
source_get = []

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

@app.route('/ds_console', methods=['POST', 'GET'])
def log_the_user_in():
    
    # login dialog, set session stuff
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
    else:
        if 'username' in session.keys():
            name=session['username']

    push_get = push_get_all()
    historic_get = historic_get_all()
    global source_get
    source_get = source_get_all()

    # separate 'live streams' from historics and their push subscriptions
    global push_get_no_historics
    push_get_no_historics = [p for p in push_get if type(p) is dict and 'hash_type' in p.keys() and p['hash_type'] != "historic"]
    hp = historic_push(historic_get,push_get)

    return render_template(
        'console.html',
        error=error,
        name=name,
        acct=account_all(),
        push=push_get_no_historics,
        historic=hp,
        source=source_get)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('apikey', None)
    return redirect(url_for('log_the_user_in'))

'''
PUSH 
'''

@app.route('/push_get_raw')
def push_get_raw():
    raw = []
    for p in push_get_no_historics:
        for r in request.args:
            print p['id']
            if p['id'] == r:
                raw.append(p)
        #look it up and jsonify the stuff.
    return jsonify(out=str(raw))


@app.route('/push_delete')
def push_delete():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            client.push.delete(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/push_stop')
def push_stop():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            client.push.stop(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/push_pause')
def push_pause():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            client.push.pause(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/push_resume')
def push_resume():
    client = Client(session['username'],session['apikey'])
    try:
        for r in request.args:
            client.push.resume(r)
        return jsonify(out="Success")
    except:
        return jsonify(out="Issues resuming")

@app.route('/push_log')
def push_log():
    client = Client(session['username'],session['apikey'])
    try:
        out = []
        for r in request.args:
            out.append(client.push.log(subscription_id=r))
        return jsonify(out=str(out))
    except:
        return jsonify(out="Issues getting log")

'''
MANAGED SOURCES
'''

@app.route('/source_get_raw')
def source_get_raw():
    raw = []
    for s in source_get:
        for r in request.args:
            if s['id'] == r:
                raw.append(s)
        #look it up and jsonify the stuff.
    return jsonify(out=str(raw))

@app.route('/source_delete')
def source_delete():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            client.managed_sources.delete(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/source_stop')
def source_stop():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            client.managed_sources.stop(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/source_start')
def source_start():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            client.managed_sources.start(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/source_log')
def source_log():
    client = Client(session['username'],session['apikey'])
    try:
        out = []
        for r in request.args:
            out.append(client.managed_sources.log(r))
        return jsonify(out=str(out))
    except:
        return jsonify(out="Issues getting log")

'''
HELPER FUNCTIONS
'''

def valid_login(user,apikey):
    try:
        client = Client(user,apikey)
        client.balance()
        return client
    except:
        return None

def historic_push(historic_get,push_get):
    ''' get dictionary of historics with list of push subscription dicts  '''
    hp = {}
    for h in historic_get:
        if type(h) is dict:
            hp[h['id']]={'historic':h}
            hp[h['id']]['subscriptions'] = []
            for p in push_get:
                if h['id'] == p['hash']:
                    hp[h['id']]['subscriptions'].append(p)
    return hp


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
        pushget = request.get('get',params=params)
        pushgetlist = [p for p in pushget['subscriptions']]
        pages = pushget['count']/per_page + 2 

        # >= 2 pages push/get response
        for i in xrange(2,pages):
            params = {
            'include_finished':1,
            'all':1,
            'order_dir':'desc',
            'per_page':per_page,
            'page':i}
            pushget = request.get('get',params=params)
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
        usage = client.usage(period='day')
        # transform usage response as a list of tuples
        usage_streams = usage['streams'].items()
        usage_period = (usage['start'],usage['end'])
        limit = (usage.headers['x-ratelimit-remaining'], usage.headers['x-ratelimit-limit'])
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
    app.run()