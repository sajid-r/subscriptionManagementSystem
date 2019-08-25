from flask import Blueprint, request, abort, make_response, jsonify, url_for
from flask_api import status
from app.payment import helper

payment= Blueprint('payment', __name__, url_prefix='/payment')

@payment.route('/add', methods=['POST'], endpoint='addPayment')
@helper.verifyPaymentDetails
def addPayment():
	paymentData = request.get_json()
	resObj = helper.createPaymentEntry(paymentData)
	if resObj!=0:
		return jsonify({'paymentId': resObj}), 200
	else:
		return jsonify({'msg': 'failed writing to DB'}), 500


@payment.route('/modify', methods=['POST'], endpoint='modifyPayment')
@helper.verifyModifyPaymentDetails
def modifyPayment():
	paymentData = request.get_json()
	paymentId = paymentData['paymentId']

	resObj = helper.checkIfPaymentExists(paymentId)
	if resObj:
		#Payment happen or not
		resObj = helper.modifyPaymentStatus(paymentData)
		if resObj!=0:
			return jsonify({'msg': 'successfully updated'}), 200
		else:
			return jsonify({'msg': 'failed writing to DB'}), 500
	else:
		return jsonify({'msg': 'paymentId does not exist'}), 404

@payment.route('/get/<paymentId>', methods=['GET'], endpoint='getPaymentDetails')
def getPaymentDetails(paymentId):
	resObj, statusCode = helper.getPaymentInfo(paymentId)
	if statusCode==1:
		return jsonify(resObj), 200
	elif statusCode==0:
		return jsonify({'msg': 'paymentId does not exist'}), 404
	elif statusCode==-1:
		return jsonify({'msg': 'encountered some problem'}), 500


