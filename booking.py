import datetime
import google.oauth2.id_token

from dateutil import tz
from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import datastore

from __main__ import app, datastore_client, firebase_request_adapter

def dateConstructor(str):

    tzinfo = tz.gettz('Europe / Dublin')
    str = list(map(int,str.split("-")))
    return datetime.datetime(str[0],str[1],str[2],0,0,0,0,tzinfo=tzinfo).replace(tzinfo=None)


@app.route('/addbooking', methods=["GET"])
def addbooking():

    roomname = request.args['roomname']

    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    
    return render_template('addbooking.html', user_data=claims,error_message=error_message, name=roomname, email=claims['email'])

@app.route('/createbooking', methods=["POST"])
def createbooking():

    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    flag = True

    roomname = request.form['roomname']
    start = request.form['start']
    end = request.form['end']

    room = datastore_client.get(datastore_client.key('RoomObject', roomname))

    start = dateConstructor(start)
    end = dateConstructor(end)

    if(len(room['bookings'])!=0):
        for booking in room['bookings']:
            if((start.replace(tzinfo=None)>=booking['start'].replace(tzinfo=None) and start.replace(tzinfo=None)<=booking['end'].replace(tzinfo=None)) or (end.replace(tzinfo=None)>=booking['start'].replace(tzinfo=None) and end.replace(tzinfo=None)<=booking['end'].replace(tzinfo=None))):
                flag = False
                return render_template('status.html', user_data=claims,error_message=error_message,status=flag)

    if(len(room['bookings'])==0):
        room['bookings'] = []
    room['bookings'].append({ 'roomname':roomname , 'start':start , 'end':end, 'user':claims['email']})
    room.update()
    datastore_client.put(room)
    return render_template('status.html', user_data=claims,error_message=error_message,status=flag)

@app.route('/editbooking', methods=['GET'])
def editbooking():

    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    roomname = request.args['roomname']
    bookingindex = int(request.args['index'])

    room = datastore_client.get(datastore_client.key('RoomObject', roomname))

    return render_template('editbooking.html', user_data=claims,error_message=error_message,name=roomname, index=bookingindex, start=room['bookings'][bookingindex]['start'].strftime("%Y-%m-%d"),end=room['bookings'][bookingindex]['end'].strftime("%Y-%m-%d"))

@app.route('/confirmbooking', methods=['POST'])
def confirmbooking():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    flag = True

    roomname = request.form['roomname']
    start = request.form['start']
    end = request.form['end']
    bookingindex = int(request.form['index'])

    room = datastore_client.get(datastore_client.key('RoomObject', roomname))

    start = dateConstructor(start)
    end = dateConstructor(end)

    if(len(room['bookings'])!=0):
        for booking in room['bookings']:
            if(booking == room['bookings'][bookingindex]):
                continue
            if((start.replace(tzinfo=None)>=booking['start'].replace(tzinfo=None) and start.replace(tzinfo=None)<=booking['end'].replace(tzinfo=None)) or (end.replace(tzinfo=None)>=booking['start'].replace(tzinfo=None) and end.replace(tzinfo=None)<=booking['end'].replace(tzinfo=None))):
                flag = False
                return render_template('status.html', user_data=claims,error_message=error_message,status=flag)

    if(len(room['bookings'])==0):
        room['bookings'] = []
    room['bookings'][bookingindex] = { 'roomname':roomname , 'start':start , 'end':end, 'user':claims['email']}
    room.update()
    datastore_client.put(room)
    return render_template('status.html', user_data=claims,error_message=error_message,status=flag)

@app.route('/filter', methods=['GET'])
def filter():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('datesearch.html', user_data=claims,error_message=error_message)

@app.route('/search', methods=['GET'])
def search():

    date = dateConstructor(request.args['date']).replace(tzinfo=None)

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
            if date>=room['bookings'][i]['start'].replace(tzinfo=None) and date<=room['bookings'][i]['end'].replace(tzinfo=None):
                room['bookings'][i]['index'] = i
                bookings.append(room['bookings'][i])

    return render_template('bookings.html', user_data=claims,error_message=error_message, bookings = bookings, user=claims['email'])

@app.route('/deletebooking', methods=['GET'])
def deletebooking():

    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    roomname = request.args['roomname']
    bookingindex = int(request.args['index'])

    room = datastore_client.get(datastore_client.key('RoomObject', roomname))

    flag = True

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    room['bookings'].pop(bookingindex)
    room.update()
    datastore_client.put(room)
    return render_template('status.html', user_data=claims,error_message=error_message,status=flag)