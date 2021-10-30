import google.oauth2.id_token
import datetime

from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import datastore
from google.cloud import storage
from user import User


datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

def doesUserExist(email):
    user = datastore_client.get(datastore_client.key('User',email))
    if user:
        return True
    return False

def getUser(email):
    user = datastore_client.get(datastore_client.key('User',email))
    temp = User(user['email'])
    if(user):
        temp.makeUser(user['directory'],user['sharedfiles'],user['files'])
    return temp

def getUserDetails(id_token):
    error_message = None
    claims = None
    times = None
    user = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
            if not doesUserExist(claims['email']):
                user = User(claims['email'])
                user.save()
            else:
                user = getUser(claims['email'])
        except ValueError as exc:
            error_message = str(exc)
    return error_message,claims,times,user
