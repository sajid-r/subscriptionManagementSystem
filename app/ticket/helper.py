from flask import request, make_response, jsonify

def response_with_obj(status, message, ticket_obj, status_code):
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
        'ticket': app_obj
    })), status_code