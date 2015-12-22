from flask import Blueprint, render_template, session, request, jsonify, make_response
from datasift import Client
from datasift.request import PartialRequest, DatasiftAuth
import datetime

push = Blueprint('push', __name__,template_folder='static')


@push.route('/get', methods=['POST', 'GET'])
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

@push.route('/get_raw')
def push_get_raw():
    raw = []
    if 'push' in session.keys():
        for p in session['push']:
            for r in request.args:
                if p['id'] == r:
                    raw.append(p)
    return jsonify(out=raw)

@push.route('/log')
def push_log():
    client = Client(session['username'],session['apikey'])
    out = []
    for r in request.args:
        try:
            out.append(client.push.log(subscription_id=r))
        except:
            # historics..
            out.append({})
    return jsonify(out=out)

@push.route('/dpus')
def push_dpus():
    hashes = []
    if 'push' in session.keys():
        for p in session['push']:
            for r in request.args:
                if p['id'] == r:
                    hashes.append(p['hash'])
    cost = dpu_cost(hashes)
    return jsonify(out=cost)

@push.route('/delete')
def push_delete():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.push.delete(r)
            success.append(r)
        except Exception, e:
            fail.append(r)
            fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@push.route('/stop')
def push_stop():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.push.stop(r)
            success.append(r)
        except Exception, e:
            fail.append(r)
            fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@push.route('/pause')
def push_pause():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.push.pause(r)
            success.append(r)
        except Exception, e:
            fail.append(r)
            fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@push.route('/resume')
def push_resume():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.push.resume(r)
            success.append(r)
        except Exception, e:
            fail.append(r)
            fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@push.route('/set_export', methods=['POST'])
def set_push_export():
    # store jquery formatted output in session data
    session['push_out'] = request.form['output'].encode('utf-8')
    response = make_response("",204)
    return response

@push.route('/get_export/output.txt')
def get_push_export():
    response = make_response(session['push_out'])
    response.headers['Content-Type'] = 'text/xml'
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=output.txt"
    return response

def push_get_all():
    ''' get list of all push subscriptions from API v1.1 '''
    pushgetlist = {
        'error':'',
        'subscriptions': []
    }

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
        pushgetlist['subscriptions'].extend([p for p in pushget['subscriptions']])
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
            pushgetlist['subscriptions'].extend([p for p in pushget['subscriptions']])

        # convert 'last request' to date format
        for p in pushgetlist['subscriptions']:
            if p['last_request']:
                p['last_request'] = datetime.datetime.fromtimestamp(p['last_request'])

        session['ratelimit'] = pushget.headers['x-ratelimit-remaining']
    except Exception, e:
        pushgetlist['error'] = e.message
    return pushgetlist['subscriptions']

def dpu_cost(hashes):
    '''get ordered dict of hourly dpu cost'''
    hash_costs = []
    try:
        client = Client(session['username'],session['apikey'])
        for h in hashes:
            dpus = client.dpu(h)
            hash_costs.append({h: dpus})
        if dpus:
            session['ratelimit'] = dpus.headers['x-ratelimit-remaining']
    except Exception, e:
        print e.message
    return hash_costs

def format_time(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S +0000")