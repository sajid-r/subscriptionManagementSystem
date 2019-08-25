from flask import Blueprint, request,abort, make_response, jsonify, url_for
from flask_api import status 
from app.subscription import helper
import requests
import json

subscription = Blueprint('subscription', __name__, url_prefix='/subscription')

@subscription.route('/addSubscription', methods=['POST'], endpoint='addSubscription')
@helper.verifySubscriptionData
def addSubscription():
	subscriptionData = request.get_json()
	
	clientId = subscriptionData['clientId']
    
	#Creating subscription ID and adding to DB
	subscriptionId = helper.createSubscriptionEntry(subscriptionData)

	#checking client exist
	resObj = helper.checkIfClientExists(clientId)
	if resObj:
		#Client Exists
		clientExists = True
		
	else:
		return jsonify({'msg': 'client id does not exist.'}), 404

	#call client->addSubscriptionId
	url = "http://127.0.0.1:5000/client/addSubscriptionId"

	payload = {
		'clientId': clientId,
		'subscriptionId': subscriptionId,
		'isLive': True
		}
	headers = {
	'Content-Type': "application/json",
	'cache-control': "no-cache",
	'Postman-Token': "e4bf6ef6-077e-4ff6-8231-abbf3ed21cb3"
	}
	payload = json.dumps(payload)
	response = requests.request("POST", url, data=payload, headers=headers)
	return(response.text,)

@subscription.route('/stopSubscription', methods=['POST'], endpoint='stopSubscription')
@helper.verifyStopSubscriptionData
def stopSubscription():
	subscriptionData = request.get_json()
	clientId = subscriptionData['clientId']
	subscriptionId = subscriptionData['subscriptionId']



	#modify_db_entry(reqBody)


	#internally call client->stopSubscription function
	url = "http://127.0.0.1:5000/client/stopSubscription"

	headers = {
		'Content-Type': "application/json",
		'cache-control': "no-cache",
		'Postman-Token': "c7b82399-60dc-4292-ac34-55ac49db8614"
		}

	payload = {
		'clientId': clientId,
		'subscriptionId': subscriptionId,
		'isLive': True
		}

	payload = json.dumps(payload)
	response = requests.request("POST", url, data=payload, headers=headers)
	return(response.text) 



@subscription.route('/modifySubscriptionServices', methods=['POST'], endpoint='modifySubscriptionServices')
@helper.verifymodifySubscriptionServicesData
def modifySubscriptionServices():
	subscriptionData = request.get_json()
	subscriptionId = subscriptionData['subscriptionId']
	clientId = subscriptionData['clientId']
	resObj = helper.checkIfClientExists(clientId)
	if resObj:
		#Client Exists
		resObj = helper.modifyClient(subscriptionData)
		if resObj!=0:
			return jsonify({'msg': 'successfully updated'}), 200
		else:
			return jsonify({'msg': 'failed writing to DB'}), 500
	else:
		return jsonify({'msg': 'client id does not exist.'}), 404

