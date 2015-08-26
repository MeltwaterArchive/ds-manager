from flask import Blueprint, render_template, session, request, jsonify, make_response
from datasift import Client
import datetime

source = Blueprint('source', __name__,template_folder='static')

@source.route('/get', methods=['POST', 'GET'])
def source_get():
    # do push/get request only when asked
    if not 'source' in session.keys() or 'reload' in request.args:
        session['source_out'] = ""
        session['source'] = source_get_all()
        session['source_reload_time'] = datetime.datetime.utcnow()
    return make_response(render_template('sources.html', source=session['source'], reload_time=format_time(session['source_reload_time'])))

@source.route('/get_raw')
def source_get_raw():
    raw = []
    if 'source' in session.keys():
        for s in session['source']:
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


def source_get_all():
    ''' get list of all managed sources '''
    sourcegetlist = []
    try:
        client = Client(session['username'],session['apikey'])
        per_page = 100

        pages = client.managed_sources.get()['count']/per_page + 2
        for i in xrange(1,pages):
            sourceget = client.managed_sources.get(per_page=per_page,page=i)
            session['ratelimit'] = sourceget.headers['x-ratelimit-remaining']
            if sourceget:
                sourcegetlist.extend([s for s in sourceget['sources']])
    except Exception, e:
        sourcegetlist = e.message
    return sourcegetlist

def format_time(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S +0000")