import os
import pathlib
import json
import urllib

import requests
import yarl
from flask import Flask, redirect, request


app = Flask(__name__)


# # with open(pathlib.Path(__file__).parent / '.app_credentials') as f:
# #     CLIENT_SECRET = f.read().strip()
CLIENT_SECRET = os.environ['OSU_CLIENT_SECET']

CLIENT_ID = 929
THIS_HOST = 'http://127.0.0.1:5000'
REDIRECT_PART = '/redirect'


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route("/redirect")
def redirected():
    print('redirected back with args: ', request.args)
    return "Going back to galaxy-integration-osu"


@app.route('/auth')
def auth():
    token = request.args.get('refresh_token')
    if token is not None:
        return "Finish. GOG Galaxy CEF should be closed"

    code = request.args.get('code')
    print('code accepted')
    if code is None:
        return 'No code were given. Fail'

    try:
        response = do_auth(code)
    except Exception as e:
        return 'An error has ocurred: ' + repr(e)
    print(response.text)
    qs = urllib.parse.urlencode(response)
    return redirect(f'/auth?{qs}')


def do_auth(code):
    """
    Response has form:
    {
        "token_type":"Bearer",
        "expires_in":86400,  # token lifetime 24h
        "access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5MjkiLCJqdGkiOiIzYThlZWZkYjA2YTc2ZTgxOWNmYjAyNTY5Y2EzYzA0ZWFiZDdkM2I3N2U4NzU1MTZmNTJkMWIyY2I1OTlhMzJmM2I4MjVmNzcyYTA1ODhlYyIsImlhdCI6MTU4NjExOTk3NSwibmJmIjoxNTg2MTE5OTc1LCJleHAiOjE1ODYyMDYzNzUsInN1YiI6IjE2NTE3MTE2Iiwic2NvcGVzIjpbImlkZW50aWZ5Il19.xxx",
        "refresh_token":"xxxxx"
    }
    decoded from token JWT: {'sub': 16517116}  # is it user id?
    """
    print('doing auth!')
    params = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': THIS_HOST + '/auth'
    }
    print(params)
    url = 'http://osu.ppy.sh/oauth/token'
    response = requests.post(url, data=params)
    response.raise_for_status()
    return json.loads(response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
