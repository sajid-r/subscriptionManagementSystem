from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.workspace.helper import response_with_id
from app.models.user import User
from app.models.workspace import Workspace
from app import logger
from app.auth.email import send_email
import os
workspace = Blueprint('workspace', __name__)

@workspace.route('/workspace/create', methods=['POST'])
@token_required
def create(current_user):
    """
        Create a workspace. Reuires login
    """
    if request.content_type == 'application/json':
        post_data = request.get_json(force=True)
        if 'name' in post_data.keys():
            workspace = Workspace(name=post_data.get('name'))
            workspace.createdBy = current_user.email_id
            workspace.create()
            current_user.workspaces.append(workspace._id)
            current_user.save()
            return response_with_id('success', 'Workspace created successfully', workspace._id, 200)
        else:
            return response('failed', 'name field required in json body', 402)

    return response('failed', 'Content-type must be json', 402)

@workspace.route('/workspace/get', methods=['GET'])
@token_required
def get(current_user):
    """
    Get a workspace by workspace id
    :return: Http Json response
    """
    wsp_id = request.args.get('workspaceId')
    if wsp_id in current_user.workspaces:
        workspace = Workspace.get_by_id(wsp_id)
        if workspace:
            return {
                'name': workspace.name,
                'id': workspace._id,
                'createdBy': workspace.createdBy,
                'createdOn': workspace.createdOn,
                'isActive': workspace.isActive,
                'projects': workspace.projects
            }
        else:
            return response('failed', 'workspace not found', 404)
    else:
        return response('failed', 'user not authorized to access workspace', 403)