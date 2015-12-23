from flask import Blueprint, render_template, session, request, jsonify, make_response
from datasift import Client
import datetime, math

source = Blueprint('source', __name__,template_folder='static')

@source.route('/get', methods=['POST', 'GET'])
def source_get():
    # do push/get request only when asked
    if not 'source' in session.keys() or 'reload' in request.args:
        session['source_out'] = ""
        session.pop('source_json',None)
        session['source_reload_time'] = datetime.datetime.utcnow()
    return make_response(render_template('sources.html', reload_time=format_time(session['source_reload_time'])))

@source.route('/get_raw')
def source_get_raw():
    raw = []
    if 'source' in session.keys():
        for s in session['source']['sources']:
            for r in request.args:
                if s['id'] == r:
                    raw.append(s)
    session['source_out'] = raw
    return jsonify(out=raw)

@source.route('/delete')
def source_delete():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.managed_sources.delete(r)
            success.append(r)
        except Exception, e:
            fail.append(r)
            fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@source.route('/stop')
def source_stop():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.managed_sources.stop(r)
            success.append(r)
        except Exception, e:
            fail.append(r)
            fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@source.route('/start')
def source_start():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            client.managed_sources.start(r)
            success.append(r)
        except Exception, e:
            fail.append(r)
            fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@source.route('/log')
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

@source.route('/token')
def source_token():
    client = Client(session['username'],session['apikey'])
    success = []
    fail = []
    fail_message = []
    for r in request.args:
        try:
            source = client.managed_sources.get(r)
            auth = source['auth']
            auth.append({"parameters":{"value":request.args[r]},"expires_at":0})
            client.managed_sources.update(
                r, source['source_type'], source['name'], source['resources'], auth, parameters=source['parameters'])
            success.append(r)
        except Exception, e:
            fail.append(r)
            fail_message.append(e.message)
    return jsonify(success=success,fail=fail,fail_message=fail_message)

@source.route('/set_export', methods=['POST'])
def set_source_export():
    # store jquery formatted output in session data
    # use encode() instead of str() to avoid encoding issues
    session['source_out'] = request.form['output'].encode('utf-8')
    response = make_response("",204)
    return response

@source.route('/get_export/output.txt')
def get_source_export():
    response = make_response(session['source_out'])
    response.headers['Content-Type'] = 'text/xml'
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=output.txt"
    return response

@source.route('/get_json')
def source_get_json():
    '''
    return json array formatted for datatables 
    '''
    if not 'source_json' in session.keys() or 'reload' in request.args or 'page' in request.args:
        session['source_json'] = []
        session['source_out'] = ""
        session['source_reload_time'] = datetime.datetime.utcnow()
        if 'page' in request.args: 
            # for some reason this doesn't work as expected
            # session['source'] = source_get_all(page=request.args['page'])
            session['source'] = source_get_all()
        else:
            session['source'] = source_get_all(page=1)

        sources = session['source']['sources']

        if sources:
            for s in sources:
                checkbox = '<input type="checkbox" class="source" id="'+s['id']+'">'

                # special html and formatting for resources, parameters, and auth
                resources = "<div class='sourcescol'><ul>"
                for r in s['resources']:
                    resources+= '<li>' + r['resource_id'] + '<ul>'
                    for p in r['parameters']:
                        # encode parameters in case of special characters
                        resources += '<li>' + p + ': ' + str(r['parameters'][p]).encode('utf-8') + '</li>'
                    resources += '</ul></li>'
                resources += "</ul></div>"

                parameters = "<ul>"
                for p in s['parameters']:
                    parameters += '<li>'+ p + ': ' + str(s['parameters'][p]) + '</li>'
                parameters += '</ul>'

                auth = "<div class='sourcescol'><ul>"
                for a in s['auth']:
                    auth += '<li>id: ' + a['identity_id']
                    for k in a['parameters']:
                        auth += '<ul><li>' + k +': ' + a['parameters'][k] + '</li></ul>'
                auth += '</li></ul></div>'

                session['source_json'].append(
                    [checkbox,
                    s['source_type'],
                    s['name'],
                    s['id'],
                    resources,
                    parameters,
                    auth,
                    str(s['created_at']),
                    s['status']])
    json = jsonify(data=session['source_json'], pages=session['source']['pages'], error=session['source']['error']) 
    return json


def source_get_all(page=0):
    ''' get list of all managed sources '''
    sources = {
        'error':'',
        'sources':[],
        'pages':0
    }
    per_page = 200

    try:
        client = Client(session['username'],session['apikey'])    

        # load all pages
        if page == 0:
            initial_get = client.managed_sources.get(per_page=per_page,page=1)
            if initial_get:
                sources['sources'].extend([i for i in initial_get['sources']])
                count = float(initial_get['count'])
                sources['pages'] = int(math.ceil(count/per_page))

                if sources['pages'] > 1:
                    for i in xrange(2,sources['pages']+1):
                        sourceget = client.managed_sources.get(per_page=per_page,page=i)
                        if sourceget:
                            sources['sources'].extend([s for s in sourceget['sources']])
        # load single page
        else:
            sourceget = client.managed_sources.get(per_page=per_page,page=page)
            count = float(sourceget['count'])
            sources['pages'] = int(math.ceil(count/per_page))
            if sourceget:
                sources['sources'].extend([s for s in sourceget['sources']])
    except Exception, e:
        sources['error'] = e.message
    return sources

def format_time(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S +0000")