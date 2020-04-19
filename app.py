import os
import pathlib
import json
import urllib

import requests
from flask import Flask, redirect, request, url_for


app = Flask(__name__)


# # with open(pathlib.Path(__file__).parent / '.app_credentials') as f:
# #     CLIENT_SECRET = f.read().strip()
CLIENT_SECRET = os.environ['OSU_CLIENT_SECET']

CLIENT_ID = 929
AUTH_OSU = '/auth/osu'


@app.route('/')
def hello():
    return 'This host serves for GOG Galaxy plugins authentication'


@app.route(AUTH_OSU)
def auth_osu():
    # TODO try to split functionality to 2 functions
    # eg. osu redirects to '/auth/osu' then this function redirect to GALAXY_FINAL_URI
    print('incoming url: ', request.url)

    token = request.args.get('refresh_token')
    if token is not None:
        return "Finish. GOG Galaxy CEF should be closed"

    code = request.args.get('code')
    if code is None:
        return 'No code were given. Fail'

    try:
        auth_params = osu_auth(code)
    except Exception as e:
        return 'An error has ocurred: ' + repr(e)
    return redirect(url_for('auth_osu', **auth_params))


def osu_auth(code):
    """
    Response has form:
    {
        "token_type":"Bearer",
        "expires_in":86400,  # token lifetime 24h
        "access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5MjkiLCJqdGkiOiIzYThlZWZkYjA2YTc2ZTgxOWNmYjAyNTY5Y2EzYzA0ZWFiZDdkM2I3N2U4NzU1MTZmNTJkMWIyY2I1OTlhMzJmM2I4MjVmNzcyYTB1ODhlYyIsImlhdCI6MTU4NjExOTk3NSwibmJmIjoxNTg2MTE5OTc1LCJleHAiOjE1ODYyMDYzNzUsInN1YiI6IjE2NTE3MTE2Iiwic2NvcGVzIjpbImlkZW50aWZ5Il19.xxx",
        "refresh_token":"xxxxx"
    }
    decoded from token JWT: {'sub': 16517116}  # is it user id?
    """
    print('Authorizing with code...')
    params = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': request.host_url.strip('/') + AUTH_OSU
    }
    url = 'http://osu.ppy.sh/oauth/token'
    response = requests.post(url, json=params)
    print(response.status_code)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
