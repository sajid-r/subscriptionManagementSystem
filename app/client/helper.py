from pymongo import MongoClient
import uuid
from dotenv import load_dotenv
import os
from flask import request, jsonify
from functools import wraps
import traceback

dotenv_path = os.path.join(os.path.abspath('.'), '.env')
load_dotenv(dotenv_path)

mongoConnectionURI=os.environ.get('mongoConnectionURI')
mongoClient = MongoClient(mongoConnectionURI)


def createClientEntry(clientData):
    clientId = 'client_'+str(uuid.uuid4())
    clientData.update({'_id':clientId, 'clientId':clientId})
    clientCollection=mongoClient['cms']['client']
    try:
        res = clientCollection.insert_one(clientData)
        print(str(res.inserted_id))
        return str(res.inserted_id)
    except:
        return 0
    

def checkIfClientExists(clientId):
    clientCollection=mongoClient['cms']['client']
    resObj = clientCollection.find_one({'_id':clientId})
    if resObj:
        return 1
    else:
        return 0


def modifyClient(clientData):
    clientCollection=mongoClient['cms']['client']

    clientId = clientData['clientId']
    clientData.pop('clientId')

    try:
        resObj = clientCollection.update_one({'_id':clientId},{'$set':clientData}, upsert=False)
        if resObj.matched_count>0:
            return 1
        else:
            return 0
    except: 
        return 0


def addSubscriptionToClient(addSubscriptionData):
    clientCollection=mongoClient['cms']['client']

    clientId = addSubscriptionData['clientId']
    addSubscriptionData.pop('clientId')

    try:
        #check if subscriptionId already exists
        resObj = clientCollection.find_one({'_id':clientId},{'subscriptions':True})
        if 'subscriptions' in resObj.keys():
            currentSubscriptions = resObj['subscriptions']
            for item in currentSubscriptions:
                if item['subscriptionId'] == addSubscriptionData['subscriptionId']:
                    return 1
        #if not present, add te subscriptionId
        resObj = clientCollection.update_one({'_id':clientId}, {'$push': {'subscriptions': addSubscriptionData}}, upsert = True)
        if resObj.matched_count>0:
            return 1
        else:
            return 0
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))
        return -1


def addPocDetails(addPocData):
    clientCollection=mongoClient['cms']['client']

    clientId = addPocData['clientId']
    addPocData.pop('clientId')

    try:
        resObj = clientCollection.update_one({'_id':clientId}, {'$set': {'clientPOC': addPocData}}, upsert = True)
        if resObj.matched_count>0:
            return 1
        else:
            return 0
    except:
        return -1


def stopSubscriptionForAClient(stopSubscriptionData):
    clientCollection=mongoClient['cms']['client']

    clientId = stopSubscriptionData['clientId']
    stopSubscriptionData.pop('clientId')

    try:
        resObj = clientCollection.find_one({'_id':clientId})
        currentSubscriptions = resObj['subscriptions']
        for item in currentSubscriptions:
            if item['subscriptionId'] == stopSubscriptionData['subscriptionId']:
                item['isLive'] = False
                break
        resObj = clientCollection.update_one({'_id':clientId}, {'$set': {'subscriptions': currentSubscriptions}}, upsert = True)
        if resObj.matched_count>0:
            return 1
        else:
            return 0
    except:
        return -1


def getClientData(clientId):
    clientCollection=mongoClient['cms']['client']

    try:
        resObj = clientCollection.find_one({'_id':clientId})
        if resObj:
            return resObj, 1
        else:
            return {}, 0
    except:
        return {}, -1




'''
    
    Request Body Verify Methods

'''

def verifyClientData(func):
    @wraps(func)
    def verifyData(*args, **kwargs):

        reqBody = request.get_json()

        if reqBody==None:
            return jsonify({'msg': 'did not receive request body'}), 400
        if 'clientName' not in reqBody.keys():
            return jsonify({'msg': 'clientName is not present in the request body.'}), 400
        if 'clientPhone' not in reqBody.keys():
            return jsonify({'msg': 'clientPhone is not present in the request body.'}), 400
        if 'clientEmail' not in reqBody.keys():
            return jsonify({'msg': 'clientEmail is not present in the request body.'}), 400

        return func(*args, **kwargs)
    return verifyData


def verifyModifyData(func):
    def verifyData(*args, **kwargs):

        reqBody = request.get_json()

        if 'clientId' not in reqBody.keys():
            return jsonify({'msg': 'clientId is not present in the request body.'}), 400
        
        return func(*args, **kwargs)
    return verifyData


def verifyAddSubscriptionData(func):
    def verifyData(*args, **kwargs):

        reqBody = request.get_json()

        if 'clientId' not in reqBody.keys():
            return jsonify({'msg': 'clientId is not present in the request body.'}), 400
        if 'subscriptionId' not in reqBody.keys():
            return jsonify({'msg': 'subscriptionId is not present in the request body.'}), 400
        
        return func(*args, **kwargs)
    return verifyData


def verifyPocData(func):
    def verifyData(*args, **kwargs):

        reqBody = request.get_json()

        if 'clientId' not in reqBody.keys():
            return jsonify({'msg': 'clientId is not present in the request body.'}), 400
        if 'clientPOC' not in reqBody.keys():
            return jsonify({'msg': 'clientPOC is not present in the request body.'}), 400
        if 'pocName' not in reqBody['clientPOC'].keys() or 'pocEmail' not in reqBody['clientPOC'].keys() or 'pocEmail' not in reqBody['clientPOC'].keys():
            return jsonify({'msg': 'clientPOC: Name, Email or Phone not present in the request body.'}), 400
        return func(*args, **kwargs)
    return verifyData