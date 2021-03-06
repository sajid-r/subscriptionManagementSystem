from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.workspace.helper import workspace_access_required
from app.project.helper import project_access_required, response_with_id, response_with_obj
from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.service import Service
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
            project = Project(name=post_data.get('name'), workspaceId=workspace_id, timezone=post_data.get('timezone'))
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
    Get a project by project id
    :return: Http Json response
    """
    project = Project.get_by_id(projectId)

    if project:
        services = project.services
        srv_payload = []
        for sid in services:
            srv = Service.get_by_id(sid)
            if srv:
                srv_obj = {'id': srv._id, 'serviceType':srv.serviceType, 'serviceMeta':srv.serviceMeta,
                'isActive': srv.isActive}
                srv_payload.append(srv_obj)
        return {
            'name': project.name,
            'id': project._id,
            'createdBy': project.createdBy,
            'createdOn': project.createdOn,
            'isActive': project.isActive,
            'services': srv_payload,
            'timezone': project.timezone
        }
    else:
        return response('failed', 'project not found', 404)
    
@project.route('/project/update', methods=['POST'])
@token_required
@project_access_required
def update(current_user, workspaceId, projectId):
    """
        Update Project
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        prj = Project.get_by_id(projectId)
        if prj:
            prj.update_project(post_data)
            res_payload = {
                'name': prj.name,
                'id': prj._id,
                'createdBy': prj.createdBy,
                'createdOn': prj.createdOn,
                'isActive': prj.isActive,
                'timezone': prj.timezone
            }
            return response_with_obj('success', 'Project updated successfully', res_payload, 200)
        else:
            response('failed', 'Project not found', 402)
    else:
        return response('failed', 'Content-type must be json', 402)

@project.route('/project/timezones', methods=['GET'])
@token_required
@project_access_required
def get_timezones(current_user, workspaceId, projectId):
    """
    Get a project by project id
    :return: Http Json response
    """
    tz_list = Project.get_timezones()

    return {
        'tzList': tz_list
    }