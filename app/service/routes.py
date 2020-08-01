from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.workspace.helper import workspace_access_required
from app.project.helper import project_access_required, response_with_id
from app.service.helper import response_with_obj, messenger_get_page_access_token
from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.service import Service
from app import logger
import os
import json
from app.models.user import User

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

            #Replcing _id with id
            service_obj = json.loads(service.to_json())
            service_obj['id'] = service_obj['_id']
            service_obj.pop('_id', None)
            
            return response_with_obj('success', 'Service created successfully', service_obj, 200)
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
    

@service.route('/service/integrations/messenger/user', methods=['POST'])
@token_required
@project_access_required
def messenger_user_handle(current_user, workspaceId, projectId):
    user_token = request.get_json(force=True).get('userToken')
    if user_token:
        response = messenger_get_page_access_token(user_token)
    else:
        return response('failed', 'userToken is required in the request payload.', 402)

    user = User.get_by_email(current_user.email_id)
    flag=0
    if isinstance(user.tokens, list):
        for item in user.tokens:
            if item.get('channel') == 'messenger':
                flag+=1
                item['token'] = user_token
        if not flag:
            user.tokens.append({'channel': 'messenger', 'token': user_token})
        user.save()
    elif not user.tokens:
            user.tokens = [{'channel': 'messenger', 'token': user_token}]
            user.save()

    return response_with_obj('success', 'Service created successfully', {'pages': response}, 200)

@service.route('/service/integrations/messenger/create', methods=['POST'])
@token_required
@project_access_required
def messenger_integration(current_user, workspaceId, projectId):
    page_token = request.get_json(force=True).get('pageToken')
    page_id = request.get_json(force=True).get('pageId')
    page_name = request.get_json(force=True).get('pageName')
    bot_id = request.get_json(force=True).get('botId')
    language_code = request.get_json(force=True).get('languageCode', 'en-US')

    if all([page_token, page_id, page_name, bot_id, language_code]):

        #check if integrations already exist for the facebook page
        existingIntegrations = Service.objects(__raw__={
                                                        'serviceMeta.channelId': str(page_id), 
                                                        'serviceMeta.channel': 'messenger'
                                                        }).count()
        #if integrations exist, disable them
        print("existingIntegrations", existingIntegrations)
        if existingIntegrations:
            services = Service.objects(__raw__={
                                                'serviceMeta.channelId': str(page_id), 
                                                'serviceMeta.channel': 'messenger'
                                                }).all()
            for item in services:
                item.isActive = False
                item.save()

        #create new service
        service = Service(  serviceType='textChannel',
                            serviceMeta={
                                'channel': 'messenger',
                                'channelId': page_id,
                                'channelName': page_name,
                                'parentBot': bot_id,
                                'accessToken': page_token,
                                'languageCode': language_code
                            }, 
                            projectId=projectId, 
                            createdBy=current_user.email_id)

        service.create()
                
        #add to project
        project = Project.get_by_id(projectId)
        project.services.append(service._id)
        project.save()

        #Replcing _id with id
        service_obj = json.loads(service.to_json())
        service_obj['id'] = service_obj['_id']
        service_obj.pop('_id', None)
        
        return response_with_obj('success', 'Service created successfully', service_obj, 200)

    else:
        return response('failed', 'Required data not found in POST body.', 402)