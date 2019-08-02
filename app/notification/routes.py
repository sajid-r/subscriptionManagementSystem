from flask import Blueprint, request, abort, make_response, jsonify, url_for
from flask_api import status
import datetime
import os
import requests, json
from app import app
import uuid
from app.notification import helper

notification = Blueprint('notification', __name__, url_prefix='/notification')

@notification.route('/sendEmail', methods=['POST'])
@helper.verifyEmailBody
def sendEmail():
    recipientEmail = request.get_json().get('emailId') 
    subject = request.get_json().get('subject')
    body = request.get_json().get('body')

    resObj = helper.sendingMail(recipientEmail, subject, body)

    return jsonify(resObj[0]), resObj[1]