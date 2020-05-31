from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.project.helper import project_access_required, response_with_id
from app.lead.helper import response_with_obj
from app.models.user import User
from app.models.lead import Lead
from app import logger
import os
import json
import math
from app import helper as util

lead = Blueprint('lead', __name__)

@lead.route('/lead/get', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
        Get Leads
    """
    pageNum = int(request.args.get('pageNum', 1))
    itemsPerPage = int(request.args.get('itemsPerPage', 25))
    
    leads_list = Lead.get_leads(pageNum, itemsPerPage, projectId)
    totalItems = Lead.get_total(projectId)
    displayName = {
                    "id": "ID",
                    "name": "Name",
                    "sex": "Sex",
                    "age": "Age",
                    "phone": "Phone",
                    "email": "Email",
                    "address": "Address",
                    "city": "City",
                    "country": "Country",
                    "channel": "Channel",
                    "createdOn": "Created On"
                }
    
    return {"leads":leads_list, "displayName":displayName, "pageNum": pageNum, "totalPages": math.ceil(totalItems/itemsPerPage), "totalEntries": totalItems}


@lead.route('/lead/add', methods=['POST'])
@token_required
@project_access_required
def add(current_user, workspaceId, projectId):
    """
        Create Leads
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        lead = Lead(
                firstName=post_data.get('firstName'),
                lastName = post_data.get(""),
                address = post_data.get('address'),
                city = post_data.get("city"),
                country = post_data.get("country"),
                notes = post_data.get("notes"),
                phone = post_data.get("phone"),
                email = post_data.get("email"),
                age = post_data.get("age"),
                dateOfBirth = post_data.get("dateOfBirth"),
                sex = post_data.get("sex"),
                channel = post_data.get("channel"),
                lastModified = util.get_current_time(),
                modifiedBy = current_user.email_id,
                # createdOn = post_data.get(None, null=True),
                createdBy = current_user.email_id,
                isDeleted = False,
                projectId=projectId
                )
        lead.create()
        res_payload = {
                'id':lead._id,
                'firstName': lead.firstName,
                'lastName': lead.lastName,
                'country': lead.country,
                'address': lead.address,
                'age': lead.age,
                'dob': lead.dateOfBirth,
                'sex': lead.sex,
                'channel': lead.channel,
                'createdOn': lead.createdOn,
                'city': lead.city,
                'phone': lead.phone,
                'email': lead.email
            }
        
        return response_with_obj('success', 'Lead created successfully', res_payload, 200)
    else:
        return response('failed', 'Content-type must be json', 402)

@lead.route('/lead/update', methods=['POST'])
@token_required
@project_access_required
def update(current_user, workspaceId, projectId):
    """
        Update Appointments
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        if 'id' not in post_data:
            return response('failed', 'Lead Id required', 402)
        else:
            lead = Lead.get_by_id(post_data.get('id'))
            if lead:
                lead.update_lead(post_data)
                res_payload = {
                    'id':lead._id,
                    'firstName': lead.firstName,
                    'lastName': lead.lastName,
                    'country': lead.country,
                    'address': lead.address,
                    'age': lead.age,
                    'dob': lead.dateOfBirth,
                    'sex': lead.sex,
                    'channel': lead.channel,
                    'createdOn': lead.createdOn,
                    'city': lead.city,
                    'phone': lead.phone,
                    'email': lead.email
                }
                return response_with_obj('success', 'Lead updated successfully', res_payload, 200)
            else:
                response('failed', 'Lead not found', 402)
    else:
        return response('failed', 'Content-type must be json', 402)

@lead.route('/lead/remove', methods=['POST'])
@token_required
@project_access_required
def remove(current_user, workspaceId, projectId):
    """
        Remove Lead By Id
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        if 'id' not in post_data:
            return response('failed', 'Lead Id required', 402)
        else:
            lead = Lead.get_by_id(post_data.get('id'))
            if lead:
                lead.delete_lead(current_user)
                res_payload = {
                    'id':lead._id,
                    'firstName': lead.firstName,
                    'lastName': lead.lastName,
                    'country': lead.country,
                    'address': lead.address,
                    'age': lead.age,
                    'dob': lead.dateOfBirth,
                    'sex': lead.sex,
                    'channel': lead.channel,
                    'createdOn': lead.createdOn,
                    'city': lead.city,
                    'phone': lead.phone,
                    'email': lead.email
                }
                return response_with_obj('success', 'Lead deleted successfully', res_payload, 200)
            else: 
                response('failed', 'Lead not found', 402)

    else:
        return response('failed', 'Content-type must be json', 402)