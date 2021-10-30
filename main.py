import datetime
import google.oauth2.id_token
from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import datastore

app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

import room
import booking

@app.route('/')
def root():

    rooms = []

    rooms = list(datastore_client.query(kind="RoomObject").fetch())

    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('main.html', user_data=claims,error_message=error_message, rooms = rooms)

if __name__ == '__main__':
    app.run(host='localhost',port=8080, debug=True)