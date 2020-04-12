from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.models.user import User
from app.models.workspace import Workspace
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
        workspaces = current_user.workspaces
        wsp_payload=[]
        for wspid in workspaces:
            print (wspid)
            wsp = Workspace.get_by_id(wspid)
            if wsp:
                wsp_name = wsp.name
                wsp_obj = {'id': wspid, 'name': wsp_name}
                wsp_payload.append(wsp_obj)

        return {
            'name': current_user.name,
            'id': current_user._id,
            'email': current_user.email_id,
            'registeredOn' : current_user.registeredOn,
            'isActive' : current_user.isActive,
            'isEmailVerified' : current_user.isEmailVerified,
            'isRemoved' : current_user.isRemoved,
            'workspaces' : wsp_payload
        }
    else:
        return response('failed', 'user not found', 404)