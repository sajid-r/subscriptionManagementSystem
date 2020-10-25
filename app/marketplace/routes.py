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
                'name': bot.name,
                'description': bot.description,
                'price' : float(bot.price),
                'tags' : bot.tags,
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


@marketplace.route('/marketplace/bot', methods=['GET'])
@token_required
@project_access_required
def get_bot(current_user, workspaceId, projectId):
    """
    Get list of all tags
    """

    botId = request.args.get("id")
    botObj = Bot.get_by_id_no_template(botId)
    payload = []
    
    return make_response(jsonify({
        'status': "success",
        'message': "Retrieved Bot Object",
        'bot': botObj
    })), 200


@marketplace.route('/marketplace/search', methods=['POST'])
@token_required
@project_access_required
def search(current_user, workspaceId, projectId):
    """
        Search Marketplace
    """
    query = request.json.get("query", None)
    filter_obj = request.json.get("filter", None)
    pageNum = int(request.args.get('pageNum', 1))
    itemsPerPage = int(request.args.get('itemsPerPage', 10))

    print("Query and Filter:", query, filter_obj)
    
    bots_list = Bot.search_bots(query, filter_obj, pageNum, itemsPerPage, projectId)
    # totalItems = Bot.get_total(projectId, query=query, filter_obj=filter_obj)
    payload = []
    print(len(bots_list))

    for bot in bots_list:
        payload.append({
            'id': bot._id,
            'name': bot.name,
            'description': bot.description,
            'price' : float(bot.price),
            'tags' : bot.tags,
            'marketplaceCardMediaUrl' : bot.marketplaceCardMediaUrl
        })
    
    return response_with_obj("success", "Successfully retrieved catalog.", payload, 200)