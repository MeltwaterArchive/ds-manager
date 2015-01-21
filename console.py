from flask import Flask, render_template,request,session,redirect,url_for,jsonify,make_response
from datasift import Client
from datasift.push import Push
from datasift.request import PartialRequest, DatasiftAuth
from flask_kvsession import KVSessionExtension
from simplekv.fs import FilesystemStore
import datetime
from collections import OrderedDict

app = Flask(__name__)

# use local filesystem for session storage instead of default client sessions
store = FilesystemStore("./data")
KVSessionExtension(store, app)

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
        'console.html',
        error=error,
        name=name,
        acct=account_all())


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    pop_session()
    return redirect(url_for('log_the_user_in'))

@app.route('/reset_push')
def reset_push():
    if 'push' in session.keys():
        session.pop('push', None)
    response = make_response("",204)
    return response

@app.route('/reset_sources')
def reset_sources():
    if 'sources' in session.keys():
        session.pop('sources', None)
    response = make_response("",204)
    return response
    

'''
PUSH 
'''

@app.route('/push_get', methods=['POST', 'GET'])
def push_get():
    # do push/get request only when asked
    if not 'push' in session.keys() or 'reload' in request.args:
        session['push_out'] = ""
        session['push_reload_time'] = datetime.datetime.utcnow()
        push_get = push_get_all()
        session['push'] = [p for p in push_get if type(p) is dict and 'hash_type' in p.keys() and p['hash_type'] != "historic"]
        # avoid another push/get if we've already loaded live steams
        session['push_historics'] = [p for p in push_get if type(p) is dict and 'hash_type' in p.keys() and p['hash_type'] == "historic"]
    return make_response(render_template('push.html', push=session['push'], reload_time=format_time(session['push_reload_time'])))

@app.route('/push_get_raw')
def push_get_raw():
    raw = []
    if 'push' in session.keys():
        for p in session['push']:
            for r in request.args:
                if p['id'] == r:
                    raw.append(p)
    return jsonify(out=raw)

@app.route('/push_log')
def push_log():
    client = Client(session['username'],session['apikey'])
    out = []
    for r in request.args:
        try:
            out.append(client.push.log(subscription_id=r))
        except:
            # historics..
            out.append("")
    return jsonify(out=out)

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
    success = []
    fail = []
    for r in request.args:
        try:
            client.push.resume(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/set_push_export', methods=['POST'])
def set_push_export():
    # store jquery formatted output in session data
    session['push_out'] = str(request.form['output'])
    response = make_response("",204)
    return response

@app.route('/get_push_export/output.txt')
def get_push_export():
    response = make_response(session['push_out'])
    response.headers['Content-Type'] = 'text/xml'
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=output.txt"
    return response

'''
HISTORICS 
'''

@app.route('/historics_get', methods=['POST', 'GET'])
def historics_get():
    # do historics/get request only when asked
    if not 'historics' in session.keys() or 'reload' in request.args:
        session['historics_reload_time'] = datetime.datetime.utcnow()
        session['historics_out'] = ""
        session['historics'] = historic_get_all()

    # only do a new push/get request if it hasn't been done/is "stale"
    if 'push_reload_time' in session.keys():
        staleness = session['historics_reload_time'] -  session['push_reload_time']
    else:
        staleness = session['historics_reload_time']
    stale_threshold = datetime.timedelta(seconds=60*15)
    if not 'push_historics' in session.keys() or 'reload' in request.args or stale_threshold < staleness:
        push_get = push_get_all()
        session['push_reload_time'] = datetime.datetime.utcnow()
        session['push_historics'] = [p for p in push_get if type(p) is dict and 'hash_type' in p.keys() and p['hash_type'] == "historic"]
    historics_push = historic_push(session['historics'], session['push_historics'])
    return make_response(render_template('historics.html', historics=historics_push, reload_time=format_time(session['historics_reload_time'])))

@app.route('/historics_get_raw')
def historics_get_raw():
    raw = []
    already_added_h = []
    if 'push_historics' in session.keys() and 'historics' in session.keys():
        for p in session['push_historics']:
            for r in request.args:
                if p['id'] == r:
                    # find the historic matching this sub
                    for h in session['historics']:
                        if p['hash'] == h['id']:
                            raw.append(h)
                            already_added_h = h['id']
                    raw.append(p)
        # historic only - no subscription
        for r in request.args:
            if not r in already_added_h:
                for h in session['historics']:
                    if r == h['id']:
                        raw.append(h)
    session['historics_out'] = raw
    return jsonify(out=raw)

@app.route('/historics_pause')
def historics_pause():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            client.historics.pause(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/historics_resume')
def historics_resume():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            client.historics.resume(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/historics_delete')
def historics_delete():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            client.historics.delete(r)
            success.append(r)
        except:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/set_historics_export', methods=['POST'])
def set_historics_export():
    # store jquery formatted output in session data
    session['historics_out'] = str(request.form['output'])
    response = make_response("",204)
    return response

@app.route('/get_historics_export/output.txt')
def get_historics_export():
    response = make_response(session['historics_out'])
    response.headers['Content-Type'] = 'text/xml'
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=output.txt"
    return response

'''
MANAGED SOURCES
'''

@app.route('/source_get', methods=['POST', 'GET'])
def source_get():
    # do push/get request only when asked
    if not 'source' in session.keys() or 'reload' in request.args:
        session['source_out'] = ""
        session['source'] = source_get_all()
        session['source_reload_time'] = datetime.datetime.utcnow()
    return make_response(render_template('sources.html', source=session['source'], reload_time=format_time(session['source_reload_time'])))

@app.route('/source_get_raw')
def source_get_raw():
    raw = []
    if 'source' in session.keys():
        for s in session['source']:
            for r in request.args:
                if s['id'] == r:
                    raw.append(s)
    session['source_out'] = raw
    return jsonify(out=raw)

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
        session['push_out'] = out
        return jsonify(out=out)
    except:
        return jsonify(out="Issues getting log")

@app.route('/source_token')
def source_token():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    for r in request.args:
        try:
            source = client.managed_sources.get(r)
            auth = source['auth']
            auth.append({"parameters":{"value":request.args[r]},"expires_at":0})
            client.managed_sources.update(
                r, source['source_type'], source['name'], source['resources'], auth, parameters=source['parameters'])
            success.append(r)
        except Exception as e:
            fail.append(r)
    return jsonify(success=success,fail=fail)

@app.route('/set_source_export', methods=['POST'])
def set_source_export():
    # store jquery formatted output in session data
    session['source_out'] = str(request.form['output'])
    response = make_response("",204)
    return response

@app.route('/get_source_export/output.txt')
def get_source_export():
    response = make_response(session['source_out'])
    response.headers['Content-Type'] = 'text/xml'
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=output.txt"
    return response

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

def pop_session():
    for k in session.keys():
        session.pop(k, None)

def historic_push(historic_get,push_get):
    ''' get dictionary of historics with list of push subscription dicts  '''
    hp = {}

    for p in push_get:
        no_hist = True
        if type(p) is dict:
            #case of multiple subscriptions for 1 historic - hist already added to hp
            if p['hash'] in hp and 'subscriptions' in hp[p['hash']]:
                hp[h['id']]['subscriptions'].append(p)
                no_hist = False
            # match subscription to historic
            else:
                for h in historic_get:
                    if p['hash'] == h['id']:
                        hp[h['id']]={'historic': h, 'subscriptions':[]}
                        hp[h['id']]['subscriptions'].append(p)
                        no_hist = False
            # case where there's no historic for this hist sub
            if no_hist:
                hp[p['hash']] = {'subscriptions':[p]}
    # case where there's no sub for the historic
    for h in historic_get:
        if type(h) is dict:
            hid = h['id']
            if not hid in hp:
                hp[hid]={'historic':h}
    
    # BLACK MAGIC - order hp by sub 'created_at', or hist 'created_at' if there's no sub
    sorted_hp = OrderedDict(
        sorted(
            hp.items(),
            key=lambda histpush: histpush[1]['subscriptions'][0]['created_at'] if 'subscriptions' in histpush[1] else histpush[1]['historic']['created_at'],
            reverse=True))
    return sorted_hp


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

        # convert 'last request' to date format
        for p in pushgetlist:
            if p['last_request']:
                p['last_request'] = datetime.datetime.fromtimestamp(p['last_request'])
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

def format_time(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S +0000")

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.debug = True
    app.run()