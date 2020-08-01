from flask import request, make_response, jsonify

def response_with_obj(status, message, app_obj, status_code):
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
        'service': app_obj
    })), status_code


def messenger_get_page_access_token(user_token):
    import requests

    url = "https://graph.facebook.com/v7.0/me/accounts"

    payload = {}
    headers = {
    'Authorization': f'Bearer {user_token}'
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    response = response.json()
    # print(response)
    payload = []
    for item in response.get('data',[]):
        if "MANAGE" in item.get('tasks'):
            access_token = item.get('access_token')
            page_name = item.get('name')
            page_id = item.get('id')

            payload.append({
                'page_name': page_name,
                "page_id": page_id,
                "access_toke": access_token
            })

    return payload