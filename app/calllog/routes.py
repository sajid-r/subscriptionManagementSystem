from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.project.helper import project_access_required, response_with_id
from app.calllog.helper import response_with_obj
from app.models.calllog import CallLog
from app import logger
import os
import json
import math
from app import helper as util

calllog = Blueprint('CallLog', __name__)

@calllog.route('/log/call/overview', methods=['GET'])
@token_required
@project_access_required
def overview(current_user, workspaceId, projectId):
    """
        Get Overview of call logs in a project
    """
    pageNum = int(request.args.get('pageNum', 1))
    itemsPerPage = int(request.args.get('itemsPerPage', 25))
    totalItems = CallLog.get_overview_total(projectId)

    callOverviewObj = CallLog.get_logs(pageNum, itemsPerPage, projectId)
    displayName = {
                    "from": "From",
                    "to": "To",
                    "duration": "Duration",
                    "timestamp": "Timestamp"
                }

    return {"callOverviewObj":callOverviewObj, "displayName":json.dumps(displayName), "pageNum": pageNum, "totalPages": math.ceil(totalItems/itemsPerPage), "totalEntries": totalItems}


@calllog.route('/log/call/get', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
        Get a call log obj
    """
    callId = request.args.get('id')
    resObj = CallLog.get_by_id(callId)
    return response_with_obj("success", "Retrieved Call Log", resObj, 200)


@calllog.route('/log/call/search', methods=['GET'])
@token_required
@project_access_required
def search(current_user, workspaceId, projectId):
    """
        Get a call log obj
    """
    _from = request.args.get('from')
    searchKeys = []
    searchKeys.append(_from)
    if '+' in _from:
        searchKeys.append(_from.replace("+",""))
    if '(' in _from or ')' in _from:
        from2 = _from.replace('(','').replace(')','')
        searchKeys.append(from2)
    if '(' in _from or ')' in _from or '+' in _from:
        from2 = _from.replace('(','').replace(')','').replace("+","")
        searchKeys.append(from2)
    resObj = CallLog.get_log_search_by_phone(searchKeys, projectId)
    return response_with_obj("success", "Retrieved Call Logs", resObj, 200)