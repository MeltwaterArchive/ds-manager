from flask import Blueprint, render_template, session, request, jsonify, make_response
from datasift import Client
from views import push
import datetime
from collections import OrderedDict

historics = Blueprint('historics', __name__,template_folder='static')

@historics.route('/get', methods=['POST', 'GET'])
def historics_get():
    # do historics/get request only when asked
    if not 'historics' in session.keys() or 'reload' in request.args:
        session['historics_reload_time'] = datetime.datetime.utcnow()
        session['historics_out'] = ""
        session['historics'] = historic_get_all()

    # determine relative staleness of historic vs live stream loads
    if 'push_reload_time' in session.keys():
        staleness = session['historics_reload_time'] -  session['push_reload_time']
    else:
        staleness = session['historics_reload_time']
    stale_threshold = datetime.timedelta(seconds=60*15)
    # only do push/get request if it hasn't been done before or reload or its stale
    if not 'push_historics' in session.keys() or 'reload' in request.args or stale_threshold < staleness:
        push_get = push.push_get_all()['subscriptions']
        session['push_reload_time'] = datetime.datetime.utcnow()
        session['push_historics'] = [p for p in push_get if type(p) is dict and 'hash_type' in p.keys() and p['hash_type'] == "historic"]
        session['push'] = [p for p in push_get if type(p) is dict and 'hash_type' in p.keys() and p['hash_type'] != "historic"]
    historics_push = historic_push(session['historics'], session['push_historics'])
    return make_response(render_template('historics.html', historics=historics_push, reload_time=format_time(session['historics_reload_time'])))

@historics.route('/get_raw')
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

@historics.route('/dpus')
def historics_dpus():
    #TODO - need to calculate historics dpu overall cost
    hashes = []
    already_added_h = []
    if 'push_historics' in session.keys():
        for p in session['push_historics']:
            for r in request.args:
                if p['id'] == r:
                    # find the historic matching this sub
                    for h in session['historics']:
                        if p['hash'] == h['id']:
                            hashes.append(h['definition_id'])
                            already_added_h = h['id']
                            break
        # historic only - no subscription
        for r in request.args:
            if not r in already_added_h:
                for h in session['historics']:
                    if r == h['id']:
                        hashes.append(h['definition_id'])
    cost = push.dpu_cost(hashes)
    return jsonify(out=cost)

@historics.route('/pause')
def historics_pause():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.historics.pause(r)
            success.append(r)
        except Exception, e:
            # see if request arg is a historic
            for ph in session['push_historics']:
                if ph['id'] == r:
                    try:
                        client.historics.pause(ph['hash'])
                        success.append(ph['hash'])
                    except Exception, e:
                        fail.append(ph['hash'])
                        fail_message.append(e.message)
                    break
            else:
                fail.append(r)
                fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@historics.route('/resume')
def historics_resume():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.historics.resume(r)
            success.append(r)
        except Exception, e:
            # see if request arg is a historic
            for ph in session['push_historics']:
                if ph['id'] == r:
                    try:
                        client.historics.resume(ph['hash'])
                        success.append(ph['hash'])
                    except Exception, e:
                        fail.append(ph['hash'])
                        fail_message.append(e.message)
                    break
            else:
                fail.append(r)
                fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@historics.route('/stop')
def historics_stop():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.historics.stop(r)
            success.append(r)
        except Exception, e:
            # see if request arg is a historic
            for ph in session['push_historics']:
                if ph['id'] == r:
                    try:
                        client.historics.stop(ph['hash'])
                        success.append(ph['hash'])
                    except Exception, e:
                        fail.append(ph['hash'])
                        fail_message.append(e.message)
                    break
            else:
                fail.append(r)
                fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@historics.route('/delete')
def historics_delete():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.historics.delete(r)
            success.append(r)
        except Exception, e:
            # see if request arg is a historic
            for ph in session['push_historics']:
                if ph['id'] == r:
                    try:
                        client.historics.delete(ph['hash'])
                        success.append(ph['hash'])
                    except Exception, e:
                        fail.append(ph['hash'])
                        fail_message.append(e.message)
                    break
            else:
                fail.append(r)
                fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@historics.route('/set_export', methods=['POST'])
def set_historics_export():
    # store jquery formatted output in session data
    session['historics_out'] = request.form['output'].encode('utf-8')
    response = make_response("",204)
    return response

@historics.route('/get_export/output.txt')
def get_historics_export():
    response = make_response(session['historics_out'])
    response.headers['Content-Type'] = 'text/xml'
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=output.txt"
    return response


def historic_push(historic_get,push_get):
    ''' get *ordered* dictionary of historics with list of push subscription dicts  '''
    hp = {}

    for p in push_get:
        no_hist = True
        if type(p) is dict:
            #case of multiple subscriptions for 1 historic - hist already added to hp
            if p['hash'] in hp and 'subscriptions' in hp[p['hash']]:
                hp[p['hash']]['subscriptions'].append(p)
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


def historic_get_all():
    ''' get list of all historics '''
    per_page = 100

    historicgetlist = []
    try:
        client = Client(session['username'],session['apikey'])
        pages = client.historics.get()['count']/per_page + 2
        for i in xrange(1,pages):
            historicget = client.historics.get(maximum=per_page,page=i)
            session['ratelimit'] = historicget.headers['x-ratelimit-remaining']
            historicgetlist.extend([h for h in historicget['data']])
    except Exception, e:
        historicgetlist = e.message
    return historicgetlist

def format_time(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S +0000")