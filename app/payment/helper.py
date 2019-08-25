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


def createPaymentEntry(paymentData):
    paymentId = 'payment_'+str(uuid.uuid4())
    paymentData.update({'_id':paymentId, 'paymentId':paymentId})
    paymentCollection=mongoClient['cms']['payment']
    try:
        res = paymentCollection.insert_one(paymentData)
        print(str(res.inserted_id))
        return str(res.inserted_id)
    except:
        return 0


def checkIfPaymentExists(paymentId):
    paymentCollection = mongoClient['cms']['payment']

    resObj = paymentCollection.find_one({'_id':paymentId})
    if resObj:
        return 1
    else:
        return 0
        

def modifyPaymentStatus(paymentData):
    paymentCollection=mongoClient['cms']['payment']

    paymentId = paymentData['paymentId']
    paymentData.pop('paymentId')

    try:
        resObj = paymentCollection.update_one({'_id':paymentId},{'$set':paymentData}, upsert=False)
        if resObj.matched_count>0:
            return 1
        else:
            return 0
    except:
        return 0


def getPaymentInfo(paymentId):
    paymentCollection=mongoClient['cms']['payment']

    try:
        resObj = paymentCollection.find_one({'_id':paymentId})
        if resObj:
            return resObj, 1
        else:
            return {}, 0
    except:
        return {}, -1


'''
    
    Request Body Verify Methods

'''

def verifyPaymentDetails(func):
    @wraps(func)
    def verifyPaymentData(*args, **kwargs):

        reqBody = request.get_json()

        if reqBody==None:
            return jsonify({'msg': 'did not receive request body'}), 400
        if 'paymentMode' not in reqBody.keys():
            return jsonify({'msg': 'paymentMode is not present in the request body.'}), 400
        if 'paymentGateway' not in reqBody.keys():
            return jsonify({'msg': 'paymentGateway is not present in the request body.'}), 400
        if 'paymentAmount' not in reqBody.keys():
            return jsonify({'msg': 'paymentAmount is not present in the request body.'}), 400
        if 'paymentCurrency' not in reqBody.keys():
            return jsonify({'msg': 'paymentCurrency is not present in the request body.'}), 400
        if 'clientId' not in reqBody.keys():
            return jsonify({'msg': 'clientId is not present in the request body.'}), 400
        if 'subscriptionId' not in reqBody.keys():
            return jsonify({'msg': 'subscriptionId is not present in the request body.'}), 400
        if 'paymentStatus' not in reqBody.keys():
            return jsonify({'msg': 'paymentStatus is not present in the request body.'}), 400
        if 'paytmentGatewayTransactionId' not in reqBody.keys():
            return jsonify({'msg': 'paytmentGatewayTransactionId is not present in the request body.'}), 400

        return func(*args, **kwargs)
    return verifyPaymentData



def verifyModifyPaymentDetails(func):
    def verifyPaymentData(*args, **kwargs):

        reqBody = request.get_json()

        if 'paymentId' not in reqBody.keys():
            return jsonify({'msg': 'paymentId is not present in the request body.'}), 400
        if 'paymentStatus' not in reqBody.keys():
            return jsonify({'msg': 'paymentStatus is not present in the request body.'}), 400
        if 'paymentMode' in reqBody.keys() or 'paymentGateway' in reqBody.keys() or 'paymentAmount' in reqBody.keys() or 'paymentCurrency' in reqBody.keys() or 'paytmentGatewayTransactionId' in reqBody.keys():
            return jsonify({'msg': 'paymentMode,paymentGateway,paymentAmount,paymentCurrency,paytmentGatewayTransactionId should not be present in the body'}), 400

        return func(*args, **kwargs)
    return verifyPaymentData



               
    

