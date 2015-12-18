from flask import Blueprint, render_template, session, request, jsonify, make_response
from datasift import Client
import datetime

account = Blueprint('account', __name__,template_folder='static')


@account.route('/get', methods=['POST', 'GET'])
def account_get():
    '''
    set account session data and render template
    '''
    if 'reload' in request.args:
        session.pop('account_json', None)
    return render_template(
        'account.html')

@account.route('/get_raw')
def account_get_raw():
    '''
    return jsonified account/get response 
    '''
    if 'identities' in session.keys():
        return jsonify(out=session['identities']['data'])
    else:
        return jsonify(out="account identity data not available..")


@account.route('/get_json')
def account_get_json():
    '''
    return json array formatted for datatables 
    '''
    if not 'account_json' in session.keys() or 'reload' in request.args:
        session['account_json'] = []
        session['identities_out'] = ""
        session['identities_reload_time'] = datetime.datetime.utcnow()
        session['identities'] = account_get_all()
        session['identities_limits']=limits_get_all()

        for s in session['identities']['data']:
            limit = None
            # add limit to json output
            for l in session['identities_limits']:
                if l['id'] == s['id']:
                    limit = "%s: %d" % (l['service'], l['total_allowance'])
            session['account_json'].append(
                [s['label'],s['id'],s['api_key'],s['created_at'],s['updated_at'],s['expires_at'],"",limit,s['master'],s['status']])
    return jsonify(data=session['account_json'],error=session['identities']['error']) 


@account.route('/get_token_json')
def account_get_token_json():
    session['identities_tokens']=tokens_get_all(session['identities']['data'])
    tokens = session['identities_tokens'] 
    # go through array created in account_get_json() and add token for each identity that has one.
    for i in session['account_json']:
        if i[9] == 'active' and i[1] in tokens.keys():
            out = ""
            for t in tokens[i[1]]:
                out += t['service'] + ": " + t['token']
            i[6] = out
    return jsonify(data=session['account_json'])


# TODO is it better to redraw the table after each request or update?

'''
class Account:
    identities = {}

    def __init__():
        pass

    def get_identities(per_page=200,page=1):
        #get all account identities 
        try:
            client = Client(session['username'],session['apikey'])
            identities_list = client.account.identity.list(page=page,per_page=per_page)
            identities.extend(identities_list['identities'])
        except Exception, e:
            identities = e.message
        return identities

    def get_tokens(services=["facebook"]):
        # returns a dictionary of identity ids with a list of tokens
        
        tokens = {}
        client = Client(session['username'],session['apikey'])
        for i in identities:
            token = []
            if i[]:
                for s in services:
                    try:
                        token.append(client.account.identity.token.get(i['id'],s))
                        tokens[i['id']] = token
                    except:
                        pass
        return tokens
'''

@account.route('/set_export', methods=['POST'])
def set_account_export():
    '''
    grab the output and set it to identities_out session for exporting
    '''
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
    per_page=200
    identities = {
        "data":{},
        "error":""
    }
    try:
        client = Client(session['username'],session['apikey'])
        identities_list = client.account.identity.list(per_page=per_page)
        identities['data'] = identities_list['identities']

        # if there are more than per_page number of identities
        while identities_list['page'] < identities_list['pages']:
            page = identities_list['page'] + 1
            identities_list = client.account.identity.list(page=page,per_page=per_page)
            identities['data'].extend(identities_list['identities'])
        #identities_keys = {i['label']: i['api_key'] for i in identities}
    except Exception, e:
        identities['error'] = e.message
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
    client = Client(session['username'],session['apikey'])
    for i in identity_ids:
        token = []
        for s in services:
            try:
                token.append(client.account.identity.token.get(i['id'],s))
                tokens[i['id']] = token
            except:
                pass
    return tokens