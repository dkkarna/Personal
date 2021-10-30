import datetime
import google.oauth2.id_token
from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import datastore

from __main__ import app, datastore_client, firebase_request_adapter

@app.route('/makenewroom', methods=['GET'])
def showroomform():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    
    return render_template('addroom.html', user_data=claims,error_message=error_message)

@app.route('/createroom', methods=['POST'])
def createroom():
    roomname = request.form['roomname']

    flag = True

    if(datastore_client.get(datastore_client.key('RoomObject', roomname))):
        flag = False

    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    
    if(flag):
        key = datastore_client.key('RoomObject',roomname)
        entity = datastore.Entity(key = key)
        entity.update({'roomname':roomname, 'bookings':[]})
        datastore_client.put(entity)
        return render_template('status.html', user_data=claims,error_message=error_message,status=flag)
    
    return render_template('status.html', user_data=claims,error_message=error_message,status=flag)

@app.route('/viewroombooking', methods=['GET'])
def getroombookings():

    roomname = request.args['roomname']
    room = datastore_client.get(datastore_client.key('RoomObject', roomname))

    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    for i in range(len(room['bookings'])):
        room['bookings'][i]['index'] = i

    return render_template('bookings.html', user_data=claims,error_message=error_message, bookings = room['bookings'], user=claims['email'])

@app.route('/viewbooking', methods=['GET'])
def getbookings():

    rooms = []
    rooms = list(datastore_client.query(kind="RoomObject").fetch())

    bookings = []

    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    for room in rooms:
        for i in range(len(room['bookings'])):
            if room['bookings'][i]['user'] == claims['email']:
                room['bookings'][i]['index'] = i
                bookings.append(room['bookings'][i])

    if 'roomname' in request.args:

        roomname = request.args['roomname']
        temp = []

        for booking in bookings:
            if booking['roomname'] == roomname:
                temp.append(booking)

        bookings = temp

    return render_template('bookings.html', user_data=claims,error_message=error_message, bookings = bookings, user=claims['email'])

@app.route('/deleteroom', methods=['GET'])
def deleteroom():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    roomname = request.args['roomname']

    room = datastore_client.get(datastore_client.key('RoomObject', roomname))

    flag = True

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    if(len(room['bookings'])!=0):
        flag = False
        return render_template('status.html', user_data=claims,error_message=error_message,status=flag)

    datastore_client.delete(room.key)
    return render_template('status.html', user_data=claims,error_message=error_message,status=flag)