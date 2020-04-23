import os
import pathlib
import json
import urllib

import requests
from flask import Flask, redirect, request, url_for


CLIENT_ID = 929
AUTH_OSU = '/auth/osu'
AUTH_OSU_FINAL = '/auth/osu/redirect'
CLIENT_SECRET = os.environ['OSU_CLIENT_SECRET']

app = Flask(__name__)


@app.route('/')
def root():
    return 'This host serves for GOG Galaxy plugins authentication'


@app.route(AUTH_OSU_FINAL)
def auth_osu_final():
    token = request.args.get('refresh_token')
    print(token)
    return "Finish. GOG Galaxy browser window should be closed"


@app.route(AUTH_OSU)
def auth_osu():
    code = request.args.get('code')
    if code is None:
        return 'Error: No `code` received!'
    try:
        auth_params = osu_auth(code)
    except Exception as e:
        return 'Error: ' + repr(e)
    return redirect(url_for('auth_osu_final', **auth_params))


def osu_auth(code):
    """Exchanges oauth `code` to `access_token`. Exemplary response:
    {
        "token_type":"Bearer",
        "expires_in":86400,  # token lifetime 24h
        "access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5MjkiLCJqdGkiOiIzYThlZWZkYjA2YTc2ZTgxOWNmYjAyNTY5Y2EzYzA0ZWFiZDdkM2I3N2U4NzU1MTZmNTJkMWIyY2I1OTlhMzJmM2I4MjVmNzcyYTB1ODhlYyIsImlhdCI6MTU4NjExOTk3NSwibmJmIjoxNTg2MTE5OTc1LCJleHAiOjE1ODYyMDYzNzUsInN1YiI6IjE2NTE3MTE2Iiwic2NvcGVzIjpbImlkZW50aWZ5Il19.xxx",
        "refresh_token":"xxxxx"
    }
    Decoded from token JWT: {'sub': 16517116}  # is it user id?
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
