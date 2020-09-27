from flask import Blueprint, request, url_for, render_template, make_response, jsonify
from app.auth.helper import response, response_auth, token_required
from app.workspace.helper import workspace_access_required
from app.project.helper import project_access_required, response_with_id
from app.models.bot import Bot
from app import logger
import os
import json
from app.marketplace.helper import response_with_obj

marketplace = Blueprint('marketplace', __name__)

@marketplace.route('/marketplace/catalog', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
    Get list of bots available in the catalog
    """

    filterObj = request.args.get("filter")
    bots = Bot.get_catalog(filterObj)
    payload = []

    if bots:
        for bot in bots:
            payload.append({
                'id': bot._id,
                'description': bot.description,
                'price' : float(bot.price),
                'marketplaceCardMediaUrl' : bot.marketplaceCardMediaUrl
            })
            print(payload)
    
    return response_with_obj("success", "Successfully retrieved catalog.", payload, 200)


@marketplace.route('/marketplace/tags', methods=['GET'])
@token_required
@project_access_required
def get_tags(current_user, workspaceId, projectId):
    """
    Get list of all tags
    """

    filterObj = request.args.get("filter")
    tags = Bot.get_tags(filterObj)
    payload = []
    
    return make_response(jsonify({
        'status': "success",
        'message': "Got the tags",
        'tags': tags
    })), 200