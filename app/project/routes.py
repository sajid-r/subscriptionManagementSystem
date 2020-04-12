from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.workspace.helper import workspace_access_required
from app.project.helper import project_access_required, response_with_id
from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app import logger
from app.auth.email import send_email
import os

project = Blueprint('project', __name__)

@project.route('/project/create', methods=['POST'])
@token_required
@workspace_access_required
def create(current_user, workspace_id):
    """
        Create a workspace. Reuires login
    """
    if request.content_type == 'application/json':
        post_data = request.get_json(force=True)
        if 'name' in post_data.keys():
            project = Project(name=post_data.get('name'), workspaceId=workspace_id)
            project.createdBy = current_user.email_id
            project.create()
            
            #add to workspace
            workspace = Workspace.get_by_id(workspace_id)
            workspace.projects.append(project._id)
            workspace.save()
            return response_with_id('success', 'Project created successfully', project._id, 200)
        else:
            return response('failed', 'name field required in json body', 402)

    return response('failed', 'Content-type must be json', 402)


@project.route('/project/get', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
    Get a project by workspace id, projectId
    :return: Http Json response
    """
    project = Project.get_by_id(projectId)
    if project:
        return {
            'name': project.name,
            'id': project._id,
            'createdBy': project.createdBy,
            'createdOn': project.createdOn,
            'isActive': project.isActive,
            'services': project.services
        }
    else:
        return response('failed', 'project not found', 404)