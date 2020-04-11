from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.models.user import User
from app import logger
import os

user = Blueprint('user', __name__)

@user.route('/user/get', methods=['GET'])
@token_required
def get(current_user):
    """
    Get a project by workspace id, projectId
    :return: Http Json response
    """
    if current_user:
        return {
            'name': current_user.name,
            'id': current_user._id,
            'email': current_user.email_id,
            'registeredOn' : current_user.registeredOn,
            'isActive' : current_user.isActive,
            'isEmailVarified' : current_user.isEmailVerified,
            'isRemoved' : current_user.isRemoved,
            'workspaces' : current_user.workspaces
        }
    else:
        return response('failed', 'user not found', 404)