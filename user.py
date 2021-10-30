import google.oauth2.id_token
import datetime

from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import datastore
from google.cloud import storage

datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

class User:
    def __init__(self, email):
        self.email = email
        self.directory = [{
            "path":"/",
            "files":[],
            "folders":[]
        }]
        self.sharedfiles = []
        self.files = []

    def makeUser(self,directory,sharedfiles,files):
        self.directory = directory
        self.sharedfiles = sharedfiles
        self.files = files

    def makeNewDirectory(self, currentdirectory, newdirectory):
        for item in self.directory:
            if item['path']==currentdirectory:
                if not newdirectory in item['folders']:
                    item['folders'].append(newdirectory)
                    self.directory.append({"path":currentdirectory[1:]+"/"+newdirectory,"files":[],"folders":[]})
                    self.save()
                    return True
        return False

    def checkDirectory(self,current,folder):
        result = []
        for i in range(len(self.directory)):
                if self.directory[i]["path"] == current[1:]+"/"+folder:
                    if len(self.directory[i]["folders"])!=0:
                        result.append(False)
                    else:
                        result.append(True)
                    if(len(self.directory[i]["files"])!=0):
                        result.append(False)
                    else:
                        result.append(True)
        return result

    def deleteNewDirectory(self,current,folder):
        flag = False
        for item in self.directory:
            if item['path']==current:
                if folder in item['folders']:
                    item['folders'].remove(folder)
                    flag = True
                    break
        if flag:
            index = -1
            for i in range(len(self.directory)):
                if self.directory[i]["path"] == current[1:]+"/"+folder:
                    index = i
                    break
            self.directory.pop(index)
            self.save()
            return True
        return False

    def save(self):
        entity_key = datastore_client.key('User',self.email)
        entity = datastore.Entity(key = entity_key)
        entity.update(self.__dict__)
        datastore_client.put(entity)
    
