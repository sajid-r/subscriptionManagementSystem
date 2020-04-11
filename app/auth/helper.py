from flask import request, make_response, jsonify
from app.models.user import User
from functools import wraps
from app import logger

def token_required(f):
    """
    Decorator function to ensure that a resource is access by only authenticated users`
    provided their auth tokens are valid
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return make_response(jsonify({
                    'status': 'failed',
                    'message': 'Provide a valid auth token'
                })), 403

        if not token:
            return make_response(jsonify({
                'status': 'failed',
                'message': 'Token is missing'
            })), 401

        try:
            decode_response = User.decode_auth_token(token) ##checks if blacklisted
            current_user = User.objects(email_id=decode_response).first()
            if not current_user:
                return make_response(jsonify({
                'status': 'failed',
                'message': 'Invalid User'
            })), 401

        except ValueError as e:
            message = str(e)
            return make_response(jsonify({
                'status': 'failed',
                'message': message
            })), 401
        except:
            message = 'Invalid token'
            if isinstance(decode_response, str):
                message = decode_response
            return make_response(jsonify({
                'status': 'failed',
                'message': message
            })), 401

        logger.bind(userId = current_user._id)
        return f(current_user, *args, **kwargs)

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