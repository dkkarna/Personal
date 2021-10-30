import google.oauth2.id_token
import datetime

from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import datastore
from google.cloud import storage
from user import User
from utils import getUser,doesUserExist,getUserDetails

app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()
CLOUD_STORAGE_BUCKET = "irvapp-bbad0.appspot.com"

@app.route('/')
def root():
    id_token = request.cookies.get("token")
    current = "/"
    if 'current' in request.args:
        current = request.args['current']
    error_message = None
    claims = None
    times = None
    user = None
    folders = []
    files = []
    shared = []
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        for item in user.directory:
            if item['path']==current:
                folders = item['folders']
                files = item['files']
        shared = user.sharedfiles
    return render_template('main.html', user_data=claims,error_message=error_message,current=current,folders=folders,files=files,shared=shared)

@app.route('/movetodirectory')
def movetodirectory():
    id_token = request.cookies.get("token")
    current = request.args['current']
    dirlist = current.split("/")
    dirlist.pop(0)
    error_message = None
    claims = None
    times = None
    items = []
    user = None
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        user.getDirectory(dirlist)
    return render_template('main.html', user_data=claims,error_message=error_message,current="/",folders=user.directory['folders'],files=user.directory['files'])

@app.route('/addfolder')
def add_directory():
    current = request.args['current']
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    error_message,claims,times,user = getUserDetails(id_token)
    return render_template('addfolder.html',user_data=claims,error_message=error_message,current=current)

@app.route('/addfile')
def add_file():
    current = request.args['current']
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    error_message,claims,times,user = getUserDetails(id_token)
    return render_template('addfile.html',user_data=claims,error_message=error_message,current=current)

@app.route('/submit_file', methods=['POST'])
def submit_file():
    current = request.form['current']
    uploaded_file = request.files['file']
    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    allblobs = gcs.list_blobs(bucket)
    for blobs in allblobs:
        if uploaded_file.filename == blobs.name:
            return render_template('cfile.html',filename=blobs.name,current=current)
    blob = bucket.blob(uploaded_file.filename)
    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        for item in user.directory:
            if item['path']==current:
                item['files'].append({"name":blob.name,"url":blob.public_url})
                user.files.append({"path":current,"name":blob.name,"url":blob.public_url,"md5":blob.md5_hash})
                user.save()
    return render_template('status.html',user_data=claims,error_message=error_message,status=True)

@app.route('/confirm_submit_file', methods=['POST'])
def confirm_submit_file():
    current = request.form['current']
    uploaded_file = request.files['file']
    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(uploaded_file.filename)
    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        for item in user.directory:
                if item['path']==current:
                    user.save()
    return render_template('status.html',user_data=claims,error_message=error_message,status=True)


@app.route('/submit_directory', methods=['POST'])
def submit_directory():
    current = request.form['current']
    ndirectory = request.form['directory']
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    status = False
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        status = user.makeNewDirectory(current,ndirectory)
    return render_template('status.html',user_data=claims,error_message=error_message,status=status)

@app.route('/delete_folder')
def delete_folder():
    current = request.args['current']
    folder = request.args['folder']
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    status = False
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        result = user.checkDirectory(current,folder)
        if not (result[0] and result[1]):
            return render_template('confirm_delete.html',user_data=claims,error_message=error_message,folders=result[0],files=result[1],current=current,folder=folder)
        status = user.deleteNewDirectory(current,folder)
    return render_template('status.html',user_data=claims,error_message=error_message,status=status)

@app.route('/confirm_delete')
def confirm_delete_folder():
    current = request.args['current']
    folder = request.args['folder']
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    status = False
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        status = user.deleteNewDirectory(current,folder)
    return render_template('status.html',user_data=claims,error_message=error_message,status=status)

@app.route('/delete_file')
def delete_file():
    current = request.args['current']
    filename = request.args['file']
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    status = False
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        temp = -1
        for item in user.directory:
            if item['path']==current:
                for i in range(len(item['files'])):
                    if item['files'][i]['name'] == filename:
                        temp = i
                        break
                item['files'].pop(temp)
        for i in range(len(user.files)):
            if user.files[i]['path'] == current and user.files[i]['name'] == filename:
                temp = i
                user.files.pop(temp)
        storage_client = storage.Client()
        bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET)
        blob = bucket.blob(filename)
        blob.delete()
        user.save()
    return render_template('status.html',user_data=claims,error_message=error_message,status=True)

@app.route('/getcurrentduplicates')
def get_current_duplicates():
    current = request.args['current']
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    status = False
    items = []
    data = []
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        for i in range(len(user.files)):
            if user.files[i]['path'] == current:
                items.append(user.files[i])
        temp = {}
        for i in range(len(items)):
            if items[i]['md5'] not in temp:
                temp[items[i]['md5']] = []
            temp[items[i]['md5']].append(i)
        for key in temp:
            if len(temp[key])>1:
                for index in temp[key]:
                    data.append(items[index])
    return render_template('dups.html',user_data=claims,error_message=error_message,data=data)

@app.route('/getAllDuplicates')
def get_duplicates():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user = None
    status = False
    items = []
    data = []
    error_message,claims,times,user = getUserDetails(id_token)
    if user!=None:
        temp = {}
        for i in range(len(user.files)):
            if user.files[i]['md5'] not in temp:
                temp[user.files[i]['md5']] = []
            temp[user.files[i]['md5']].append(i)
        for key in temp:
            if len(temp[key])>1:
                for index in temp[key]:
                    data.append(user.files[index])
    return render_template('dups.html',user_data=claims,error_message=error_message,data=data)

@app.route('/share_file')
def share_file():
    current = request.args['current']
    filename = request.args['file']
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    error_message,claims,times,user = getUserDetails(id_token)
    return render_template('share.html',user_data=claims,error_message=error_message,current=current,file=filename)

@app.route('/shared')
def shared():
    current = request.args['current']
    filename = request.args['file']
    shareduser = request.args['email']
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    status = False
    error_message,claims,times,user = getUserDetails(id_token)
    newuser = getUser(shareduser)
    if newuser!=None:
        for f in user.files:
            if f['path'] == current and f['name']==filename:
                newuser.sharedfiles.append(f)
                newuser.save()
                status = True
    return render_template('status.html',user_data=claims,error_message=error_message,status=status)

if __name__ == '__main__':
    app.run(host='localhost',port=8080, debug=True)
