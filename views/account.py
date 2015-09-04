from flask import Blueprint, render_template, session, request, jsonify, make_response
from datasift import Client
import datetime

account = Blueprint('account', __name__,template_folder='static')


@account.route('/get', methods=['POST', 'GET'])
def account_get():
    if not 'identities' in session.keys() or 'reload' in request.args:
        session['identities_out'] = ""
        session['identities_reload_time'] = datetime.datetime.utcnow()
        session['identities'] = account_get_all()
        session['identities_limits']=limits_get_all()
        session['identities_tokens']=tokens_get_all(session['identities'])
    return render_template(
        'account.html',
        raw=session['identities'],
        limits=session['identities_limits'],
        tokens=session['identities_tokens'])

@account.route('/get_raw')
def account_get_raw():
    if 'identities' in session.keys():
        return jsonify(out=session['identities'])
    else:
        return jsonify(out="account identity data not available..")

@account.route('/set_export', methods=['POST'])
def set_account_export():
    # store jquery formatted output in session data
    session['identities_out'] = request.form['output'].encode('utf-8')
    response = make_response("",204)
    return response

@account.route('/get_export/output.txt')
def get_account_export():
    response = make_response(session['identities_out'])
    response.headers['Content-Type'] = 'text/xml'
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=output.txt"
    return response

# account IDENTITIES 
def account_get_all():
    ''' get all account identities '''
    identities = {}
    try:
        client = Client(session['username'],session['apikey'])
        identities_list = client.account.identity.list(per_page=100)
        identities = identities_list['identities']
        #identities_keys = {i['label']: i['api_key'] for i in identities}
    except Exception, e:
        identities = e.message
        # identities = "[ account identities not available ]"
    return identities

def limits_get_all(services=["facebook"]):
    ''' single list of all limits for all services '''
    limits = []
    try:
        client = Client(session['username'],session['apikey'])
        # for now, just do facebook
        for s in services:
            limits_list = client.account.identity.limit.list(s)
            limits += limits_list["limits"]
    except Exception, e:
        client = e.message
    return limits

def tokens_get_all(identity_ids,services=["facebook"]):
    '''
    returns a dictionary of identity ids with a list of tokens
    '''
    tokens = {}
    try:
        client = Client(session['username'],session['apikey'])
        for i in identity_ids:
            token = []
            for s in services:
                token.append(client.account.identity.token.get(i['id'],s))
            tokens[i['id']] = token
    except Exception, e:
        client = e.message
    print "tokens", tokens
    return tokens