from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.workspace.helper import workspace_access_required
from app.project.helper import project_access_required, response_with_id
from app.service.helper import response_with_obj
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
        Create a service. Reuires login
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
            
            return response_with_id('success', 'Service created successfully', service._id, 200)
        else:
            return response('failed', 'Required data not found in POST body.', 402)

    return response('failed', 'Content-type must be json', 402)


@service.route('/service/get', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
    Get a service by service id or project id
    :return: Http Json response
    """
    serviceId = request.args.get('serviceId')
    if serviceId:
         #Get by Service ID
        service = Service.get_by_id(serviceId)
        if service:
            return {
                'serviceType': service.serviceType,
                'id': service._id,
                'createdBy': service.createdBy,
                'createdOn': service.createdOn,
                'isActive': service.isActive,
                'serviceMeta': service.serviceMeta
            }
        else:
            return response('failed', 'service not found', 404)
    else:
        #Get by Project ID
        project = Project.get_by_id(projectId)
        services = project.services
        payload = []
        for service_id in services:
            service = Service.get_by_id(service_id)
            payload.append({"id": service_id, 
                            "serviceType": service.serviceType, 
                            "isActive": service.isActive,
                            "serviceMeta": service.serviceMeta})
        
        return {'services':payload} 

@service.route('/service/deactivate', methods=['POST'])
@token_required
@project_access_required
def deactivate(current_user, workspaceId, projectId):
    """
    Deactivate a service
    Service ID Is mandatory
    :return: Http Json response
    """
    if request.content_type == 'application/json':
        serviceId = request.get_json(force=True).get('serviceId')
        if serviceId:
            service = Service.get_by_id(serviceId)
            if service:
                service.deactivate()
                res_payload = {
                    'serviceType': service.serviceType,
                    'id': service._id,
                    'createdBy': service.createdBy,
                    'createdOn': service.createdOn,
                    'isActive': service.isActive,
                    'serviceMeta': service.serviceMeta
                }

                return response_with_obj('success', 'Service deactivated successfully', res_payload, 200)
            else:
                return response('failed', 'service not found', 404)
        else:
            return response('failed', 'Service ID is required in the request payload.', 402)

    else:
        return response('failed', 'Content-type must be json', 402)



@service.route('/service/activate', methods=['POST'])
@token_required
@project_access_required
def activate(current_user, workspaceId, projectId):
    """
    Deactivate a service
    Service ID Is mandatory
    :return: Http Json response
    """
    if request.content_type == 'application/json':
        serviceId = request.get_json(force=True).get('serviceId')
        if serviceId:
            service = Service.get_by_id(serviceId)
            if service:
                service.activate()
                res_payload = {
                    'serviceType': service.serviceType,
                    'id': service._id,
                    'createdBy': service.createdBy,
                    'createdOn': service.createdOn,
                    'isActive': service.isActive,
                    'serviceMeta': service.serviceMeta
                }

                return response_with_obj('success', 'Service activated successfully', res_payload, 200)
            else:
                return response('failed', 'service not found', 404)
        else:
            return response('failed', 'Service ID is required in the request payload.', 402)

    else:
        return response('failed', 'Content-type must be json', 402)
    