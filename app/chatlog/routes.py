from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.project.helper import project_access_required, response_with_id
from app.chatlog.helper import response_with_obj
from app.models.chatlog import ChatLog
from app import logger
import os
import json
import math
from app import helper as util

chatlog = Blueprint('chatlog', __name__)

@chatlog.route('/log/chat/get', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
        Get Chats for a conversation
    """

    conversationId = request.args.get('conversationId')
    
    if not conversationId:
        return response('failed', 'Need conversation Id in query params.', 402)

    chatLogObj = ChatLog.get_by_id(conversationId)
    
    return response_with_obj("success", "Chat Log retrieved", chatLogObj, 200)


@chatlog.route('/log/chat/overview', methods=['POST'])
@token_required
@project_access_required
def overview(current_user, workspaceId, projectId):
    """
        Get Overview of conversations in a project
    """
    pageNum = int(request.args.get('pageNum', 1))
    itemsPerPage = int(request.args.get('itemsPerPage', 25))
    filter_obj = request.json.get("filter", {})
    totalItems = ChatLog.get_overview_total(projectId, filter_obj)

    chatOverviewObj = ChatLog.get_log_overview(filter_obj, pageNum, itemsPerPage, projectId)
    displayName = {
                    "externalId": "User ID",
                    "lastMessage": "Last Message",
                    "lastMessageTimestamp": "Last Active",
                    "channel": "Channel"
                }

    return {"chatOverviewObj":chatOverviewObj, "displayName":json.dumps(displayName), "pageNum": pageNum, "totalPages": math.ceil(totalItems/itemsPerPage), "totalEntries": totalItems}
