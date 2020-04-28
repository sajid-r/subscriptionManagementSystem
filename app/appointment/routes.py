from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.project.helper import project_access_required, response_with_id
from app.appointment.helper import response_with_obj
from app.models.user import User
from app.models.appointment import Appointment
from app import logger
import os
import json

appointment = Blueprint('appointment', __name__)

@appointment.route('/appointment/get', methods=['GET'])
@token_required
@project_access_required
def get(current_user, workspaceId, projectId):
    """
        Get Appointments
    """
    start = request.args.get('start')
    end = request.args.get('end')

    if start == None or end == None:
        return response('failed', 'Start and End Timestamp required.', 402)
    else:
        appointment_list = Appointment.get_appointments(start, end, projectId)
        return {"appointments":appointment_list}


@appointment.route('/appointment/add', methods=['POST'])
@token_required
@project_access_required
def add(current_user, workspaceId, projectId):
    """
        Create Appointments
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        app = Appointment(
                participantName=post_data.get('participantName'),
                startDate=post_data.get('startDate'),
                endDate=post_data.get('endDate'),
                participant=post_data.get('participant'),
                appointmentChannel=post_data.get('appointmentChannel'),
                participantPhone=post_data.get('participantPhone'),
                projectId=projectId
                )
        app.create()
        res_payload = {
                'id':app._id,
                'start': app.startDate,
                'end': app.endDate,
                'title': app.participantName,
                'phone': app.participantPhone,
                'email': app.participantEmail,
                'isActive': app.isActive,
                'cssClass': 'ACTIVE' if app.isActive else 'DELETED'
            }
        
        return response_with_obj('success', 'Appointment created successfully', res_payload, 200)
    else:
        return response('failed', 'Content-type must be json', 402)

@appointment.route('/appointment/update', methods=['POST'])
@token_required
@project_access_required
def update(current_user, workspaceId, projectId):
    """
        Update Appointments
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        if 'id' not in post_data:
            return response('failed', 'Appointment Id required', 402)
        else:
            app = Appointment.get_by_id(post_data.get('id'))
            if app:
                app.update_appointment(post_data)
                res_payload = {
                    'id':app._id,
                    'start': app.startDate,
                    'end': app.endDate,
                    'title': app.participantName,
                    'phone': app.participantPhone,
                    'email': app.participantEmail,
                    'isActive': app.isActive,
                    'cssClass': 'ACTIVE' if app.isActive else 'DELETED'
                }
                return response_with_obj('success', 'Appointment updated successfully', res_payload, 200)
            else:
                response('failed', 'Appointment not found', 402)
    else:
        return response('failed', 'Content-type must be json', 402)

@appointment.route('/appointment/remove', methods=['POST'])
@token_required
@project_access_required
def remove(current_user, workspaceId, projectId):
    """
        Remove Appointment By Id
    """
    if request.content_type == 'application/json':
        post_data = request.get_json()
        if 'id' not in post_data:
            return response('failed', 'Appointment Id required', 402)
        else:
            app = Appointment.get_by_id(post_data.get('id'))
            if app:
                app.delete_appointment(current_user)
                res_payload = {
                    'id':app._id,
                    'start': app.startDate,
                    'end': app.endDate,
                    'title': app.participantName,
                    'phone': app.participantPhone,
                    'email': app.participantEmail,
                    'isActive': app.isActive,
                    'cssClass': 'ACTIVE' if app.isActive else 'DELETED'
                }
                return response_with_obj('success', 'Appointment deleted successfully', res_payload, 200)
            else: 
                response('failed', 'Appointment not found', 402)

    else:
        return response('failed', 'Content-type must be json', 402)