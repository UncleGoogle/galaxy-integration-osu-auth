import pathlib
import json
import urllib

import requests
import yarl
from flask import Flask, redirect, request


app = Flask(__name__)


# # with open(pathlib.Path(__file__).parent / '.app_credentials') as f:
# #     CLIENT_SECRET = f.read().strip()
CLIENT_ID = 929
CLIENT_SECRET = 'dev'
THIS_HOST = 'http://127.0.0.1:5000'


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route("/redirect")
def redirected():
    print('redirected back with args: ', request.args)
    return "Going back to galaxy-integration-osu"


@app.route("/redirect_osu")
def redirected_osu():
    print('not here dude with args: ', request.args)
    return "Not here dude :("


@app.route('/auth', methods = ['POST'])
def user():
    code = request.args.get('code')
    if code is None:
        return 'No code were given. Fail'
    try:
        response = do_auth(code)
    except Exception as e:
        return 'An error has ocurred: ' + repr(e)
    refresh = response['refresh']
    # qs = urllib.parse.urlencode(response)  # all stuff
    print('after auth')
    return redirect(f'/redirect?refresh_token={refresh}')


def do_auth(code):
    params = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': THIS_HOST + '/redirect_osu'
    }
    url = 'http://osu.ppy.sh/oauth/token'
    response = requests.post(url, params=params)
    response.raise_for_status()
    return json.loads(response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
