from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.workspace.helper import workspace_access_required
from app.project.helper import project_access_required, response_with_id
from app.playground.helper import response_with_obj
from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.playground import Playground
from app.models.bot import Bot
from app import logger
import os
import json

playground = Blueprint('playground', __name__)

@playground.route('/playground/create', methods=['POST'])
@token_required
@project_access_required
def create(current_user, workspaceId, projectId):
    """
        Create a playground. Reuires login
    """
    if request.content_type == 'application/json':
        post_data = request.get_json(force=True)
        required_keys = ['botId']
        if all(name in post_data for name in required_keys):
            bot = Bot.get_by_id(post_data.get('botId')) #bot id is fronteous generated. bot is is for a specific version of agent from dialogflow
            if not bot:
                return response('failed', 'Bot not found in the marketplace', 404)
            playground = Playground(playgroundType='bot',
                            playgroundMeta=bot.botMeta, 
                            projectId=projectId, 
                            createdBy=current_user.email_id)
            
            playground.create()
            
            #add to project
            # project = Project.get_by_id(projectId)
            # project.services.append(playground._id)
            # project.save()

            #Replcing _id with id
            playground_obj = json.loads(playground.to_json())
            playground_obj['id'] = playground_obj['_id']
            playground_obj.pop('_id', None)
            
            return response_with_obj('success', 'Playground created successfully', playground_obj, 200)
        else:
            return response('failed', 'Required data not found in POST body.', 402)

    return response('failed', 'Content-type must be json', 402)


@playground.route('/playground/get', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
    Get a playground by playground id or project id
    :return: Http Json response
    """
    playgroundId = request.args.get('playgroundId')
    parentMarketplaceBot = request.args.get('parentMarketplaceBot')
    publishedServiceId = request.args.get('publishedServiceId')
    if playgroundId:
         #Get by Playground ID
        playground = Playground.get_by_id(playgroundId)
        if playground:
            return {
                'playgroundType': playground.playgroundType,
                'id': playground._id,
                'projectId' : playground.projectId,
                'createdOn' : playground.createdOn,
                'createdBy': playground.createdBy,
                'isRemoved' : playground.isRemoved,
                'removedOn' : playground.removedOn,
                'parentMarketplaceBot' : playground.parentMarketplaceBot,
                'publishedServiceId' : playground.publishedServiceId,
                'lastModified': playground.lastModified,
                'playgroundMeta': playground.playgroundMeta,
                'isPublished' : playground.isPublished,
                'publishedOn' : playground.publishedOn
            }
        else:
            return response('failed', 'playground not found', 404)
    elif parentMarketplaceBot:
        print(parentMarketplaceBot)
        #Get by Project ID & parentMarketplaceBot
        playgrounds = Playground.get_by_project_and_parent_bot(projectId, parentMarketplaceBot)
        payload = []
        for playground in playgrounds:
            payload.append({
                'playgroundType': playground.playgroundType,
                'id': playground._id,
                'projectId' : playground.projectId,
                'createdOn' : playground.createdOn,
                'createdBy': playground.createdBy,
                'isRemoved' : playground.isRemoved,
                'removedOn' : playground.removedOn,
                'parentMarketplaceBot' : playground.parentMarketplaceBot,
                'publishedServiceId' : playground.publishedServiceId,
                'lastModified': playground.lastModified,
                'playgroundMeta': playground.playgroundMeta,
                'isPublished' : playground.isPublished,
                'publishedOn' : playground.publishedOn
            })
        
        return {'playgrounds':payload}
    elif publishedServiceId:
        plagrounds = Playground.get_by_project_and_published_service(projectId, publishedServiceId)
        payload = []
        for playground in playgrounds:
            payload.append({
                'playgroundType': playground.playgroundType,
                'id': playground._id,
                'projectId' : playground.projectId,
                'createdOn' : playground.createdOn,
                'createdBy': playground.createdBy,
                'isRemoved' : playground.isRemoved,
                'removedOn' : playground.removedOn,
                'parentMarketplaceBot' : playground.parentMarketplaceBot,
                'publishedServiceId' : playground.publishedServiceId,
                'lastModified': playground.lastModified,
                'playgroundMeta': playground.playgroundMeta,
                'isPublished' : playground.isPublished,
                'publishedOn' : playground.publishedOn
            })
        
        return {'playgrounds':payload}
    else:
        #Get by Project ID
        playgrounds = Playground.get_by_project_id(projectId)
        payload = []
        for playground in playgrounds:
            payload.append({
                'playgroundType': playground.playgroundType,
                'id': playground._id,
                'projectId' : playground.projectId,
                'createdOn' : playground.createdOn,
                'createdBy': playground.createdBy,
                'isRemoved' : playground.isRemoved,
                'removedOn' : playground.removedOn,
                'parentMarketplaceBot' : playground.parentMarketplaceBot,
                'publishedServiceId' : playground.publishedServiceId,
                'lastModified': playground.lastModified,
                'playgroundMeta': playground.playgroundMeta,
                'isPublished' : playground.isPublished,
                'publishedOn' : playground.publishedOn
            })
        
        return {'playgrounds':payload} 

@playground.route('/playground/publish', methods=['POST'])
@token_required
@project_access_required
def publish(current_user, workspaceId, projectId):
    """
    Publish a playground
    Playground ID Is mandatory
    :return: Http Json response
    """
    if request.content_type == 'application/json':
        playgroundId = request.get_json(force=True).get('playgroundId')
        priceContract = request.get_json(force=True).get('priceContract')
        if playgroundId:
            playground = Playground.get_by_id(playgroundId)
            if playground:
                srv_id = playground.publish(projectId, current_user, priceContract)
                return response('success', srv_id, 200)
            else:
                return response('failed', 'playground not found', 404)
        else:
            return response('failed', 'Playground ID is required in the request payload.', 402)
    else:
        return response('failed', 'Content-type must be json', 402)    


@playground.route('/playground/update', methods=['POST'])
@token_required
@project_access_required
def update(current_user, workspaceId, projectId):
    """
    Update a playground
    Playground ID Is mandatory
    :return: Http Json response
    """
    if request.content_type == 'application/json':
        playgroundId = request.get_json(force=True).get('playgroundId')
        update_obj = request.get_json(force=True).get('updateObj')
        if playgroundId:
            playground = Playground.get_by_id(playgroundId)
            if playground:
                playground.update(update_obj)
                playgroundObj = {
                                'playgroundType': playground.playgroundType,
                                'id': playground._id,
                                'createdBy': playground.createdBy,
                                'lastModified': playground.lastModified,
                                'playgroundMeta': playground.playgroundMeta
                            }
                return response_with_obj('success', 'Playground updated successfully', playgroundObj, 200)
            else:
                return response('failed', 'playground not found', 404)
        else:
            return response('failed', 'Playground ID is required in the request payload.', 402)
    else:
        return response('failed', 'Content-type must be json', 402)    


@playground.route('/playground/delete', methods=['POST'])
@token_required
@project_access_required
def delete(current_user, workspaceId, projectId):
    """
    Delete a playground if playground is unpublished else does nothing
    Playground ID Is mandatory
    :return: Http Json response
    """
    if request.content_type == 'application/json':
        playgroundId = request.get_json(force=True).get('playgroundId')
        if playgroundId:
            playground = Playground.get_by_id(playgroundId)
            if playground:
                if playground.isPublished:
                    return response('failed', 'Cannot delete a playground that has been published', 400)
                else:
                    playground.isRemoved = True
                    playground.save()
                    return response('success', 'Playground deleted.', 200)
            else:
                return response('failed', 'playground not found', 404)
        else:
            return response('failed', 'Playground ID is required in the request payload.', 402)
    else:
        return response('failed', 'Content-type must be json', 402)   