from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.workspace.helper import workspace_access_required
from app.project.helper import project_access_required, response_with_id
from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.service import Service
from app import logger
import os

service = Blueprint('service', __name__)

@service.route('/service/create', methods=['POST'])
@token_required
@project_access_required
def create(current_user, workspaceId, projectId):
    """
        Create a workspace. Reuires login
    """
    if request.content_type == 'application/json':
        post_data = request.get_json(force=True)
        required_keys = ['serviceType', 'serviceMeta']
        if all(name in post_data for name in required_keys):

            service = Service(serviceType=post_data.get('serviceType'),
                            serviceMeta=post_data.get('serviceMeta'), 
                            projectId=projectId, 
                            createdBy=current_user.email_id)
            
            service.create()
            
            #add to project
            project = Project.get_by_id(projectId)
            project.services.append(service._id)
            project.save()
            
            return response_with_id('success', 'Service created successfully', project._id, 200)
        else:
            return response('failed', 'Required data not found in POST body.', 402)

    return response('failed', 'Content-type must be json', 402)


@service.route('/service/get', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
    Get a project by workspace id, projectId
    :return: Http Json response
    """
    serviceId = request.args.get('serviceId')
    service = Service.get_by_id(serviceId)
    if service:
        return {
            'serviceType': service.serviceType,
            'id': service._id,
            'createdBy': service.createdBy,
            'createdOn': service.createdOn,
            'isActive': service.isActive,
            'serviceMeta': service.services
        }
    else:
        return response('failed', 'service not found', 404)