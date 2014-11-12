from flask import Flask, render_template,request,session
from datasift import Client
from datasift.push import Push
from datasift.request import PartialRequest, DatasiftAuth

app = Flask(__name__)

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

def valid_login(user,apikey):
    try:
        client = Client(user,apikey)
        client.balance()
        return client
    except:
        return None

@app.route('/ds_console', methods=['POST', 'GET'])
def log_the_user_in():
    client = Client(session['username'],session['apikey'])
    pushget = client.push.get(include_finished=True)
    pushgetstr = [ str(p) for p in pushget['subscriptions']]

    # custom push get request, so we can pass all to API v.1.1 
    # should only be for internal accounts
    request = PartialRequest(DatasiftAuth(session['username'],session['apikey']),prefix='push')
    params = {'include_finished':1,'all':1,'per_page':100}
    pushget = request.get('get',params)
    pushgetstr = [ str(p) for p in pushget['subscriptions']]

    historicget = client.historics.get()
    historicget = client.historics.get(maximum=historicget['count'])
    historicgetstr = [str(h) for h in historicget['data']]
    return render_template('console.html', 
        name=session['username'],push=pushgetstr, historic=historicgetstr)


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.debug = True
    app.run()