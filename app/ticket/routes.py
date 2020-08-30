from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.project.helper import project_access_required, response_with_id
from app.ticket.helper import response_with_obj
from app.models.user import User
from app.models.ticket import Ticket
from app import logger
import os
import json
import math
from app import helper as util

ticket = Blueprint('ticket', __name__)

@ticket.route('/ticket/get', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
        Get Tickets
    """
    pageNum = int(request.args.get('pageNum', 1))
    itemsPerPage = int(request.args.get('itemsPerPage', 25))
    
    tickets_list = Ticket.get_tickets(pageNum, itemsPerPage, projectId)
    totalItems = Ticket.get_total(projectId)
    displayName = {
                    "id": "ID",
                    "status": "Status",
                    "category": "Category",
                    "channel": "Channel",
                    "name": "Name",
                    "phone": "Phone",
                    "email": "Email",
                    "modifiedBy": "Modified By",
                    "createdOn": "Created On",
                    "lastModified": "Last Modified",                    
                }
    
    return {"tickets":tickets_list, "displayName":json.dumps(displayName), "pageNum": pageNum, "totalPages": math.ceil(totalItems/itemsPerPage), "totalEntries": totalItems}
    # return {"tickets":tickets_list, "pageNum": pageNum, "totalPages": math.ceil(totalItems/itemsPerPage), "totalEntries": totalItems}


@ticket.route('/ticket/search', methods=['POST'])
@token_required
@project_access_required
def search(current_user, workspaceId, projectId):
    """
        Search Tickets
    """
    query = request.json.get("query","")
    filter_obj = request.json.get("filter", {})
    pageNum = int(request.args.get('pageNum', 1))
    itemsPerPage = int(request.args.get('itemsPerPage', 25))

    print("Query and Filter:", query, filter_obj)
    
    tickets_list = Ticket.search_tickets(query, filter_obj, pageNum, itemsPerPage, projectId)
    totalItems = Ticket.get_total(projectId, query=query, filter_obj=filter_obj)
    displayName = {
                    "id": "ID",
                    "status": "Status",
                    "category": "Category",
                    "channel": "Channel",
                    "name": "Name",
                    "phone": "Phone",
                    "email": "Email",
                    "modifiedBy": "Modified By",
                    "createdOn": "Created On",
                    "lastModified": "Last Modified",                    
                }
    
    return {"tickets":tickets_list, "displayName":json.dumps(displayName), "pageNum": pageNum, "totalPages": math.ceil(totalItems/itemsPerPage), "totalEntries": totalItems}
    # return {"tickets":tickets_list, "pageNum": pageNum, "totalPages": math.ceil(totalItems/itemsPerPage), "totalEntries": totalItems}


@ticket.route('/ticket/add', methods=['POST'])
@token_required
@project_access_required
def add(current_user, workspaceId, projectId):
    """
        Create Tickets
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        ticket = Ticket(
                firstName=post_data.get('firstName'),
                lastName = post_data.get(""),
                notes = post_data.get("notes"),
                phone = post_data.get("phone"),
                email = post_data.get("email"),
                channel = post_data.get("channel"),
                lastModified = util.get_current_time(),
                modifiedBy = current_user.email_id,
                category = post_data.get("category"),
                status = post_data.get("status"),
                # createdOn = post_data.get(None, null=True),
                createdBy = current_user.email_id,
                isDeleted = False,
                projectId=projectId
                )
        ticket.create()
        res_payload = {
                'id':ticket._id,
                'firstName': ticket.firstName,
                'lastName': ticket.lastName,
                'channel': ticket.channel,
                'createdOn': ticket.createdOn,
                'status': ticket.status,
                'notes' : ticket.notes,
                'category': ticket.category,
                'phone': ticket.phone,
                'email': ticket.email
            }
        
        return response_with_obj('success', 'Ticket created successfully', res_payload, 200)
    else:
        return response('failed', 'Content-type must be json', 402)

@ticket.route('/ticket/update', methods=['POST'])
@token_required
@project_access_required
def update(current_user, workspaceId, projectId):
    """
        Update Appointments
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        if 'id' not in post_data:
            return response('failed', 'Ticket Id required', 402)
        else:
            ticket = Ticket.get_by_id(post_data.get('id'))
            if ticket:
                ticket.update_ticket(post_data, current_user)
                res_payload = {
                    'id':ticket._id,
                    'firstName': ticket.firstName,
                    'lastName': ticket.lastName,
                    'category': ticket.category,
                    'status': ticket.status,
                    'notes': ticket.notes,
                    'channel': ticket.channel,
                    'createdOn': ticket.createdOn,
                    'phone': ticket.phone,
                    'email': ticket.email
                }
                return response_with_obj('success', 'Ticket updated successfully', res_payload, 200)
            else:
                response('failed', 'Ticket not found', 402)
    else:
        return response('failed', 'Content-type must be json', 402)

@ticket.route('/ticket/remove', methods=['POST'])
@token_required
@project_access_required
def remove(current_user, workspaceId, projectId):
    """
        Remove Ticket By Id
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        if 'id' not in post_data:
            return response('failed', 'Ticket Id required', 402)
        else:
            ticket = Ticket.get_by_id(post_data.get('id'))
            if ticket:
                ticket.delete_ticket(current_user)
                res_payload = {
                    'id':ticket._id,
                    'firstName': ticket.firstName,
                    'lastName': ticket.lastName,
                    'category': ticket.category,
                    'status': ticket.status,
                    'notes': ticket.notes,
                    'channel': ticket.channel,
                    'createdOn': ticket.createdOn,
                    'phone': ticket.phone,
                    'email': ticket.email
                }
                return response_with_obj('success', 'Ticket deleted successfully', res_payload, 200)
            else: 
                response('failed', 'Ticket not found', 402)

    else:
        return response('failed', 'Content-type must be json', 402)

@ticket.route('/ticket/categories', methods=['GET'])
@token_required
@project_access_required
def get_categories(current_user, workspaceId, projectId):
    """
        Get all Categories in Tickets
    """
    categories = Ticket.get_categories(projectId)
    
    return {"categories":categories}