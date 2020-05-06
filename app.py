import os
import logging
import pathlib
import json
import urllib

import requests
from flask import Flask, redirect, request, url_for, jsonify

from exceptions import HttpError


CLIENT_ID = 929
CLIENT_SECRET = os.environ['OSU_CLIENT_SECRET']


app = Flask(__name__)


@app.errorhandler(HttpError)
def handle_custom_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def root():
    return 'This host serves for GOG Galaxy plugins authentication'


@app.route('/auth/osu/redirect')
def auth_osu_final():
    assert request.args.get('refresh_token')
    return "Finish. GOG Galaxy browser window should be closed"


@app.route('/auth/osu')
def auth_osu():
    code = request.args.get('code')
    if code is None:
        return 'Error: No `code` received!'
    try:
        auth_params = osu_auth_token(
            grant_type='authorization_code',
            code=code,
            redirect_uri=request.base_url
        )
    except Exception as e:
        return 'Error: ' + repr(e)
    return redirect(url_for('auth_osu_final', **auth_params))


@app.route('/auth/osu/refresh', methods = ['POST'])
def auth_osu_refresh():
    tkn = request.json.get('refresh_token')
    if tkn is None:
        raise HttpError('Error: No `refresh_token` received!')
    try:
        new_tokens = osu_auth_token(
            grant_type='refresh_token',
            refresh_token=tkn
        )
    except requests.HTTPError as e:
        raise HttpError(str(e), status_code=e.response.status_code)
    except Exception as e:
        logging.exception(e)
        raise HttpError(repr(e), status_code=500)
    else:
        return jsonify(new_tokens)


def osu_auth_token(**custom):
    """Gets `access_token`. Exemplary response:
    {
        "token_type":"Bearer",
        "expires_in":86400,  # token lifetime 24h
        "access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5MjkiLCJqdGkiOiIzYThlZWZkYjA2YTc2ZTgxOWNmYjAyNTY5Y2EzYzA0ZWFiZDdkM2I3N2U4NzU1MTZmNTJkMWIyY2I1OTlhMzJmM2I4MjVmNzcyYTB1ODhlYyIsImlhdCI6MTU4NjExOTk3NSwibmJmIjoxNTg2MTE5OTc1LCJleHAiOjE1ODYyMDYzNzUsInN1YiI6IjE2NTE3MTE2Iiwic2NvcGVzIjpbImlkZW50aWZ5Il19.xxx",
        "refresh_token":"xxxxx"
    }
    """
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    params.update(custom)
    url = 'http://osu.ppy.sh/oauth/token'
    response = requests.post(url, json=params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
