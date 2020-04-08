from flask import request, make_response, jsonify
from app.models.user import User
from functools import wraps
from app import logger

def workspace_access_required(f):
    """
    Decorator function to ensure that a resource is access by only authenticated users who have access to the workspace`
    provided their auth tokens are valid
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        post_data = request.get_json()
        params = request.args

        if request.method == 'POST':
            if not 'workspaceId' in post_data.keys():
                return make_response(jsonify({
                    'status': 'failed',
                    'message': 'Workpsace Id required'
                })), 403
            else:
                workspaceId = post_data.get('workspaceId')
        
        if request.method == 'GET':
            if not 'workspaceId' in params.keys():
                return make_response(jsonify({
                    'status': 'failed',
                    'message': 'Workpsace Id required'
                })), 403
            else:
                workspaceId = params.get('workspaceId')


        if not workspaceId in current_user.workspaces:
            return make_response(jsonify({
                    'status': 'failed',
                    'message': 'User is not authorized to access the workspace'
                })), 403

        logger.bind(userId = current_user._id)
        return f(current_user, workspaceId, *args, **kwargs)

    return decorated_function


def response(status, message, status_code):
    """
    Helper method to make an Http response
    :param status: Status
    :param message: Message
    :param status_code: Http status code
    :return:
    """
    return make_response(jsonify({
        'status': status,
        'message': message
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