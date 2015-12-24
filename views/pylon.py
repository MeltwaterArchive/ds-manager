from flask import Blueprint, render_template, session, request, jsonify, make_response
from datasift import Client
from views import account
import datetime

pylon = Blueprint('pylon', __name__,template_folder='static')


@pylon.route('/get', methods=['POST', 'GET'])
def pylon_get():
    # clear session variables on reload
    if 'reload' in request.args:
        session.pop('pylon_json',None)
        session.pop('pylon',None)
        session['pylon_out'] = ""
        session['pylon_reload_time'] = datetime.datetime.utcnow()
    if not 'python_reload_time' in session:
        session['pylon_reload_time'] = datetime.datetime.utcnow()
    return render_template(
        'PYLON.html',
        reload_time=format_time(session['pylon_reload_time']))

@pylon.route('/get_raw')
def pylon_get_raw():
    if 'pylon' in session.keys():
        return jsonify(out=session['pylon'])
    else:
        return jsonify(out="pylon data not available..")

@pylon.route('/start')
def pylon_start():
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        # split the id of the checkboxes on _ to get hash and identity id, so we can stop it
        hash_idid = r.split('_')
        if not 'identities' in session:
            session['identities'] = account.account_get_all()['data']
        for i in session['identities']:
            try:
                if i['id'] == hash_idid[1]:
                    client = Client(session['username'],i['api_key'])
                    client.pylon.start(hash_idid[0])
                    success.append(hash_idid[0])
            except Exception, e:
                fail.append(hash_idid[0])
                fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@pylon.route('/stop')
def pylon_stop():
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        # split the id of the checkboxes on _ to get hash and identity id, so we can stop it
        hash_idid = r.split('_')
        if not 'identities' in session:
            session['identities'] = account.account_get_all()['data']
        for i in session['identities']:
            try:
                if i['id'] == hash_idid[1]:
                    client = Client(session['username'],i['api_key'])
                    client.pylon.stop(hash_idid[0])
                    success.append(hash_idid[0])
            except Exception, e:
                fail.append(hash_idid[0])
                fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@pylon.route('/set_export', methods=['POST'])
def set_pylon_export():
    # store jquery formatted output in session data
    session['pylon_out'] = request.form['output'].encode('utf-8')
    response = make_response("",204)
    return response

@pylon.route('/get_export/output.txt')
def get_pylon_export():
    response = make_response(session['pylon_out'])
    response.headers['Content-Type'] = 'text/xml'
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=output.txt"
    return response

@pylon.route('/get_json')
def pylon_get_json():
    '''
    return json array formatted for datatables 
    '''
    if not 'pylon_json' in session.keys() or 'reload' in request.args or 'page' in request.args:
        session['pylon_json'] = []
        session['pylon_out'] = ""
        session['pylon_reload_time'] = datetime.datetime.utcnow()
        if 'page' in request.args:
            session['pylon'] = pylon_get_all(page=int(request.args['page']))
        # by default just load the first page
        else:
            session['pylon'] = pylon_get_all(page=1)

        recordings = session['pylon']['recordings']

        if recordings:
            for s in recordings:
                checkbox = '<input type="checkbox" class="pylon" id="'+s['hash']+'_'+s['identity_id']+'">'
                session['pylon_json'].append(
                    [checkbox,
                    s['name'],
                    s['hash'],
                    s['identity_label'],
                    str(s['start']),
                    str(s['end']),
                    s['remaining_index_capacity'],
                    s['volume'],
                    s['status']])
    json = jsonify(data=session['pylon_json'], error=session['pylon']['error']) 
    return json


def pylon_get_all(page=0):
    ''' get all PYLON recordings for all accounts '''
    recordings = {
        "error":"",
        "recordings":[],
    }
    per_page=200

    try:
        client = Client(session['username'],session['apikey'])
        recs = client.pylon.list(page=page,per_page=per_page)

        if page == 0:
            page = 2
            # if there are more than per_page number of recordings for an account
            while len(recs) == per_page:
                recordings["recordings"].extend(recs)
                recs =  client.pylon.list(page=page,per_page=per_page)
                page += 1
            recordings["recordings"].extend(recs)
        else:
            recordings["recordings"].extend(recs)

        # add identity label information to recordings if it's already loaded
        if 'identities' in session and 'data' in session['identities']:
            for r in recordings["recordings"]:
                for i in session['identities']['data']:
                    if r['identity_id'] == i['id']:
                        r['identity_label'] = i['label']
        else:
            # identities not loaded = don't bother with label
            for r in recordings["recordings"]:
                r['identity_label'] = r['identity_id']
    except Exception, e:
        recordings["error"] = e.message
    return recordings

    # old approach - goes through each identity
    '''
    try:
        # need identities to get PYLON recording
        if not 'identities' in session:
            session['identities'] = account.account_get_all()['data']
        if not 'identities_limits' in session:
            session['identities_limits']= account.limits_get_all()
        
        # if identities session is a string, then PYLON is not available. Just use identity error message
        if isinstance(session['identities'], basestring):
            recordings = session['identities']
        else:
            for i in session['identities']:
                # inactive identities don't have a pylon/get response
                if i['status'] == 'active':
                    idclient = Client(session['username'],i['api_key'])
                    # in the case that there's an issue with an identity, we get an error when trying to get a recording
                    try:
                        recs=idclient.pylon.list(per_page=per_page)
                        page = 2
                        # if there are more than per_page number of recordings for an identity
                        while len(recs) == per_page:
                            for r in recs:
                                # add identity label to each recording
                                r['identity_label'] = i['label']
                            recordings.append(recs)
                            recs =  idclient.pylon.list(page=page,per_page=per_page)
                            page += 1
                        for r in recs:
                            # add identity label to each recording
                            r['identity_label'] = i['label']
                        recordings.append(recs)

                    except Exception, e:
                        # no recordings
                        pass
                    
    except Exception, e:
        recordings = e.message
    return recordings
    '''

def format_time(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S +0000")