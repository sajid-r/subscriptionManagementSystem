from flask import Blueprint, request, abort, make_response, jsonify, url_for
from flask_api import status
import datetime
import os
import requests, json
from app import app
import uuid
from app.notifiction import helper

notification = Blueprint('notification', __name__)

@notification.route('/sendEmail', methods=['GET'])
@helper.verifyEmailBody
def sendEmail():
    return(helper.sendingMail('guna.hk444@gmail.com'))