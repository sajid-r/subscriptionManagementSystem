from flask import Blueprint, request, abort, make_response, jsonify, url_for
from flask_api import status
from app.client import helper

client = Blueprint('client', __name__, url_prefix='/client')

@client.route('/add', methods=['POST'], endpoint='addClient')
@helper.verifyClientData
def addClient():
    clientData = request.get_json()
    resObj = helper.createClientEntry(clientData)
    if resObj!=0:
        return jsonify({'clientId': resObj}), 200
    else:
        return jsonify({'msg': 'failed writing to DB'}), 500


@client.route('/modify', methods=['POST'], endpoint='modifyClient')
@helper.verifyModifyData
def modifyClient():
    clientData = request.get_json()
    clientId = clientData['clientId']

    resObj = helper.checkIfClientExists(clientId)
    if resObj:
        #Client Exists
        resObj = helper.modifyClient(clientData)
        if resObj!=0:
            return jsonify({'msg': 'successfully updated'}), 200
        else:
            return jsonify({'msg': 'failed writing to DB'}), 500
    else:
        return jsonify({'msg': 'client id does not exist.'}), 404


@client.route('/addSubscriptionId', methods=['POST'], endpoint='addSubscriptionToClient')
@helper.verifyAddSubscriptionData
def addSubscriptionToClient():
    addSubscriptionData = request.get_json()

    resObj = helper.addSubscriptionToClient(addSubscriptionData)
    if resObj==1:
        return jsonify({'msg': 'subscription added successfully'}), 200
    elif resObj==0:
        return jsonify({'msg': 'clientId or subscriptionId does not exist.'}), 404
    elif resObj==-1:
        return jsonify({'msg': 'encountered some problem.'}), 500


@client.route('/addPocDetails', methods=['POST'], endpoint='addPocDetails')
@helper.verifyPocData
def addPocDetails():
    addPocData = request.get_json()

    resObj = helper.addPocDetails(addPocData)
    if resObj==1:
        return jsonify({'msg': 'pocDetails added successfully'}), 200
    elif resObj==0:
        return jsonify({'msg': 'clientId does not exist.'}), 404
    elif resObj==-1:
        return jsonify({'msg': 'encountered some problem.'}), 500


@client.route('/stopSubscription', methods=['POST'], endpoint='stopSubscriptionForAClient')
@helper.verifyAddSubscriptionData
def stopSubscriptionForAClient():
    stopSubscriptionData = request.get_json()

    resObj = helper.stopSubscriptionForAClient(stopSubscriptionData)
    if resObj==1:
        return jsonify({'msg': 'subscription info updated'}), 200
    elif resObj==0:
        return jsonify({'msg': 'clientId or subscriptionId does not exist.'}), 404
    elif resObj==-1:
        return jsonify({'msg': 'encountered some problem.'}), 500


@client.route('/get/<clientId>', methods=['GET'], endpoint='getClientData')
def getClientData(clientId):
    resObj, statusCode = helper.getClientData(clientId)
    if statusCode==1:
        return jsonify(resObj), 200
    elif statusCode==0:
        return jsonify({'msg': 'clientId does not exist.'}), 404
    elif statusCode==-1:
        return jsonify({'msg': 'encountered some problem.'}), 500