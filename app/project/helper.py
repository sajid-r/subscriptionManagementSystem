from flask import request, make_response, jsonify
from app.models.user import User
from functools import wraps
from app import logger
from app.models.workspace import Workspace

def project_access_required(f):
    """
    Decorator function to ensure that a resource is access by only authenticated users who have access to the workspace`
    provided their auth tokens are valid
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        params = request.args

        if request.method == 'POST':
            #first checks in post body and then query params as fallback
            post_data = request.get_json()
            # print(post_data.keys())
            if not 'workspaceId' in post_data.keys() or not 'projectId' in post_data.keys():
                # print("######")
                if not 'workspaceId' in params.keys() or not 'projectId' in params.keys():
                    return make_response(jsonify({
                        'status': 'failed',
                        'message': 'Workpsace Id and Project Id required'
                    })), 403
                else:
                    workspaceId = params.get('workspaceId')
                    projectId = params.get('projectId')
            else:
                # print("1234123412341234")
                workspaceId = post_data.get('workspaceId')
                projectId = post_data.get('projectId')
        
        elif request.method == 'GET':
            if not 'workspaceId' in params.keys() or not 'projectId' in params.keys():
                return make_response(jsonify({
                    'status': 'failed',
                    'message': 'Workpsace Id and Project Id required'
                })), 403
            else:
                workspaceId = params.get('workspaceId')
                projectId = params.get('projectId')


        if not workspaceId in current_user.workspaces:
            return make_response(jsonify({
                    'status': 'failed',
                    'message': 'User is not authorized to access the workspace'
                })), 403

        workspace = Workspace.get_by_id(workspaceId)

        if not projectId in workspace.projects:
            return make_response(jsonify({
                    'status': 'failed',
                    'message': 'User is not authorized to access the project'
                })), 403

        logger.bind(userId = current_user._id)
        return f(current_user, workspaceId, projectId, *args, **kwargs)

    return decorated_function


def response_with_id(status, message, prjid, status_code):
    """
    Helper method to make an Http response
    :param status: Status
    :param message: Message
    :param status_code: Http status code
    :return:
    """
    return make_response(jsonify({
        'status': status,
        'message': message,
        'id': prjid
    })), status_code

def response_with_obj(status, message, payload, status_code):
    return make_response(jsonify({
        'status': status,
        'message': message,
        'project': payload
    })), status_code


def response_auth(status, message, token, expiry, status_code=200):
    """
    Make a Http response to send the auth token
    :param status: Status
    :param message: Message
    :param token: Authorization Token
    :param status_code: Http status code
    :return: Http Json response
    """
    return jsonify({
        'status': status,
        'message': message,
        'auth_token': token,
        'expiry': expiry
    })