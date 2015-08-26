from flask import Blueprint, render_template, current_app, session, request, jsonify, make_response
from datasift import Client
import datetime

usage = Blueprint('usage', __name__,template_folder='static')

@usage.route("/get")
def get_usage():
  if not 'usage' in session.keys() or 'reload' in request.args:
    session['usage_out'] = ""
    session['usage_reload_time'] = datetime.datetime.utcnow()
    session['usage'] = usage_all()
  return render_template(
      'usage.html',
      acct=session['usage'],
      reload_time=format_time(session['usage_reload_time']))


@usage.route('/get_raw')
def usage_get_raw():
    if 'usage' in session.keys():
        return jsonify(out=session['usage'])
    else:
        return jsonify(out="usage data not available..")

@usage.route('/set_export', methods=['POST'])
def set_usage_export():
    # store jquery formatted output in session data
    session['usage_out'] = request.form['output'].encode('utf-8')
    response = make_response("",204)
    return response

@usage.route('/get_export/output.txt')
def get_usage_export():
    response = make_response(session['usage_out'])
    response.headers['Content-Type'] = 'text/xml'
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=output.txt"
    return response

def usage_all():
    ''' get usage and rate limit '''
    usage = {}
    try:
        client = Client(session['username'],session['apikey'])
        usage = client.usage(period='day')
        session['ratelimit'] = usage.headers['x-ratelimit-remaining']
    except Exception, e:
        usage = e.message
    return usage

def format_time(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S +0000")