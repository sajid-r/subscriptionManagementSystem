from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.project.helper import project_access_required, response_with_id
from app.lead.helper import response_with_obj
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
    pageNum = int(request.args.get('pageNum', 1))
    
    if not conversationId:
        return response('failed', 'Need conversation Id in query params.', 402)

    chatLogObj = ChatLog.get_by_id(conversationId)
    
    return chatLogObj


@chatlog.route('/log/chat/overview', methods=['GET'])
@token_required
@project_access_required
def overview(current_user, workspaceId, projectId):
    """
        Get Overview of conversations in a project
    """
    pageNum = int(request.args.get('pageNum', 1))
    itemsPerPage = int(request.args.get('itemsPerPage', 25))
    totalItems = Lead.get_overview_total(projectId)

    chatOverviewObj = ChatLog.get_log_overview(pageNum, itemsPerPage, projectId)

    return {"chatOverviewObj":chatOverviewObj, "pageNum": pageNum, "totalPages": math.ceil(totalItems/itemsPerPage), "totalEntries": totalItems}
