from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth, token_required
from app.project.helper import project_access_required, response_with_id
from app.models.user import User
from app.models.appointment import Appointment
from app import logger
import os

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
                projectId=post_data.get('projectId')
                )
        app.create()
        return response_with_id('success', 'Appointment created successfully', app._id, 200)
    else:
        return response('failed', 'Content-type must be json', 402)