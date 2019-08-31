from pymongo import MongoClient
import uuid
from dotenv import load_dotenv
import os
from flask import request, jsonify
from functools import wraps
import traceback
import requests
import json

dotenv_path = os.path.join(os.path.abspath('.'), '.env')
load_dotenv(dotenv_path)

mongoConnectionURI=os.environ.get('mongoConnectionURI')
mongoClient = MongoClient(mongoConnectionURI)

def createSubscriptionEntry(subscriptionData):
	subscriptionId = 'subscription_'+str(uuid.uuid4())
	subscriptionData.update({'_id':subscriptionId, 'subscriptionId':subscriptionId})
	subscriptionCollection=mongoClient['cms']['subscription']
	try:
		res = subscriptionCollection.insert_one(subscriptionData)
		print(str(res.inserted_id))
		return str(res.inserted_id)
	except:
		return 0
	
def checkIfSubscriptionExists(subscriptionId):
	subscriptionCollection=mongoClient['cms']['subscription']
	resObj = subscriptionCollection.find_one({'_id':subscriptionId})
	if resObj:
		return 1
	else:
		return 0

def checkIfClientExists(clientId):
	clientCollection=mongoClient['cms']['client']
	resObj = clientCollection.find_one({'_id':clientId})
	if resObj:
		return 1
	else:
		return 0

def modifySubscription(subscriptionData):
	subscriptionCollection=mongoClient['cms']['subscription']

	subscriptionId = subscriptionData['subscriptionId']
	subscriptionData.pop('subscriptionId')

	try:
		resObj = subscriptionCollection.update_one({'_id':subscriptionId},{'$set':subscriptionData}, upsert=False)
		if resObj.matched_count>0:
			return 1
		else:
			return 0
	except: 
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


def stopSubscriptionForASubscription(stopSubscriptionData):
	subscriptionCollection=mongoClient['cms']['subscription']
	
	subscriptionId = stopSubscriptionData['subscriptionId']
	stopSubscriptionData.pop('subscriptionId')

	try:
		resObj = subscriptionCollection.find_one({'_id':subscriptionId})
		currentSubscriptions = resObj['subscriptions']
		for item in currentSubscriptions:
			if item['subscriptionId'] == stopSubscriptionData['subscriptionId']:
				item['isLive'] = False
				break
		resObj = subscriptionCollection.update_one({'_id':subscriptionId}, {'$set': {'subscriptions': currentSubscriptions}}, upsert = True)
		if resObj.matched_count>0:
			return 1
		else:
			return 0
	except:
		return -1




'''

	Verify DATA

'''

def verifySubscriptionData(func):
	@wraps(func)
	def verifyData(*args, **kwargs):

		reqBody = request.get_json()

		if reqBody==None:
			return jsonify({'msg': 'did not receive request body'}), 400
		if 'subscriptionServicesEnabled' not in reqBody.keys():
			return jsonify({'msg': 'subscriptionServicesEnabled is not present in the request body.'}), 400
		if 'subscriptionLive' not in reqBody.keys():
			return jsonify({'msg': 'subscriptionLive is not present in the request body.'}), 400

		return func(*args, **kwargs)
	return verifyData


def verifyStopSubscriptionData(func):
	@wraps(func)
	def verifyData(*args, **kwargs):

		reqBody = request.get_json()

		if reqBody==None:
			return jsonify({'msg': 'did not receive request body'}), 400
		if 'clientId' not in reqBody.keys():
			return jsonify({'msg': 'clientId is not present in the request body.'}), 400
		if 'subscriptionId' not in reqBody.keys():
			return jsonify({'msg': 'subscriptionId is not present in the request body.'}), 400
		

		return func(*args, **kwargs)
	return verifyData



def verifymodifySubscriptionServicesData(func):
	@wraps(func)
	def verifyData(*args, **kwargs):

		reqBody = request.get_json()

		if reqBody==None:
			return jsonify({'msg': 'did not receive request body'}), 400
		if 'clientId' not in reqBody.keys():
			return jsonify({'msg': 'clientId is not present in the request body.'}), 400
		if 'subscriptionId' not in reqBody.keys():
			return jsonify({'msg': 'subscriptionId is not present in the request body.'}), 400
		if 'serviceInfo' not in reqBody.keys():
			return jsonify({'msg': 'serviceInfo is not present in the request body.'}), 400

		return func(*args, **kwargs)
	return verifyData
