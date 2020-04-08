from flask import Blueprint, request, url_for, render_template
import re
from app.auth.helper import response, response_auth
from app.models.user import User, BlackListToken
from app import logger
from app.auth.email import send_email
import os

auth = Blueprint('auth', __name__)


@auth.route('/auth/login', methods=['POST'])
def login():
    """
    Login a user if the supplied credentials are correct.
    :return: Http Json response
    """
    if request.content_type == 'application/json':
        post_data = request.get_json(force=True)
        email = post_data.get('email')
        password = User.encode_password(post_data.get('password'))
        
        if re.match(r"[^@]+@[^@]+\.[^@]+", email) and password:
            user = User.get_by_email(email)
            # password = User.encode_password(password)
            if user and not user.isEmailVerified:
                return response('failed', 'Email not verified. Sign-up again to verify email.', 400)
            if user and not user.isRemoved:

                if not (user.registeredOn or user.isActive):
                    user.password = password
                    user.sign_up(userObj=post_data)

                if password == user.password:
                    logger.bind(userId = user._id)
                    accessToken = user.get_auth_token()
                    return response_auth(
                        'success',
                        'Successfully logged In',
                        accessToken,
                        os.getenv('AUTH_TOKEN_EXPIRY_SECONDS'),
                        200)
                else:
                    return response(
                        'failed',
                        'Wrong Password',
                        403)
            else:
                logger.error('USER_NOT_FOUND', email=email)
                return response('failed', 'User not found', 401)
        return response('failed', 'Missing or wrong email format or password is less than four characters', 400)
    return response('failed', 'Content-type must be json', 402)

@auth.route('/auth/signup', methods=['POST'])
def signup():
    """
    Signup a user using name, email, password.
    :return: Http Json response
    """
    
    if request.content_type == 'application/json':
        post_data = request.get_json(force=True)
        email = post_data.get('email')
        password = User.encode_password(post_data.get('password'))
        name = post_data.get('name')
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            user = User.get_by_email(email)
            if user and user.isActive and user.isEmailVerified:
                return response('failed', 'Email already registered. Use the Sign-in option', 401)
            if user and user.isActive and not user.isEmailVerified:
                token = user.get_auth_token()
                confirm_url = url_for('auth.verify', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url)
                subject = "Fronteous Arena - Confirm your email address"
                send_email(user.email_id, subject, html)

                logger.bind(userId = user._id)
                return response_auth(
                    'success',
                    'Successfully signed up.',
                    None,
                    None,
                    200)

            else:
                user = User(email_id = email, name = name, password = password)  
                user.sign_up(userObj=post_data)

                if not user.isEmailVerified:           #If email is not verified. Not email at this stage wil be verified only for invited users coming through invitation token
                    token = user.get_auth_token()
                    confirm_url = url_for('auth.verify', token=token, _external=True)
                    html = render_template('activate.html', confirm_url=confirm_url)
                    subject = "Fronteous Arena - Confirm your email address"
                    send_email(user.email_id, subject, html)

                logger.bind(userId = user._id)
                return response_auth(
                    'success',
                    'Successfully signed up.',
                    None,
                    None,
                    200)
        return response('failed', 'Missing or wrong email format or password is less than four characters', 400)
    return response('failed', 'Content-type must be json', 402)


@auth.route('/auth/verify', methods=['GET'])
def verify():
    verifyToken = request.args.get('token')

    email = User.decode_verify_token(verifyToken)
    user = User.get_by_email(email)
    if user and not user.isEmailVerified:
        user.modify(isEmailVerified=True)
        return response('success', 'Email has been verified.', 200)
    if user and user.isEmailVerified:
        return response('success', 'Account already confirmed. Please login.', 200)
    else:
        return response('failed', 'Invalid Token. Email not found', 401)
    

@auth.route('/auth/logout', methods=['POST'])
def logout():
    """
    Try to logout a user using a token
    :return:
    """
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            return response('failed', 'Provide a valid auth token', 401)
        else:
            # decoded_token_response = User.decode_auth_token(auth_token)
            token = BlackListToken(auth_token)
            token.blacklist()
            return response('success', 'Successfully logged out', 200)

    return response('failed', 'Provide an authorization header', 403)
