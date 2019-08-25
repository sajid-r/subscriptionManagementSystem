import boto3
from botocore.exceptions import ClientError
from flask import request, jsonify
import re
def sendingMail(recepiantmail, subject, body):
    # Replace guna.hk444@gmail.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "Pravallika <pravallika.juturu1@gmail.com>"

    # Replace guna.hk444@gmail.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = recepiantmail

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    #ConfigurationSetName=CONFIGURATION_SET
    #CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-west-2"

    # The subject line for the email.
    SUBJECT = subject

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("PythonProject \r\n"
                 "This email was sent for testing using the AWS SDK for Python (Boto)."
                )
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>Python Project  SES Test (SDK for Python)</h1>
      <h1>Second line testig</h1
    </body>
    </html>
                """            

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong. 
    except ClientError as e:
        response = e.response['Error']['Message']
        return response, 500
    else:
        response = "Email sent!"
    return response, 200


def verifyEmailId(emailId):
    if (re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$',emailId))==None:
        return jsonify({'msg': 'emailId is not valid.'}), 400

def verifyEmailBody(func):
    def verifyBody(*args, **kwargs):
        body = request.get_json()
        print(type(body))
        print(list(body.keys()))
        if 'emailId' in list(body.keys()):
            emailId = body['emailId']
            verifyEmailId(emailId)
        else:
            return jsonify({'msg': 'emailId is not present in the request body.'}), 400
        if 'body' not in list(body.keys()):
            return jsonify({'msg': 'body is not present in the request body.'}), 400
        if 'subject' in list(body.keys()):
            if type(body.get('subject')).__name__!='str':
                return jsonify({'msg': 'subject is not in string format.'}), 400
        else:
            return jsonify({'msg': 'subject is not present in the request body.'}), 400
        #Checking 'cc' has valid emailIds or not
        if 'cc' in list(body.keys()):
            verifyEmailId('cc')

        #checking 'signature' is in text or html format or not
        if "signature" in list(body.keys()):
            if type(body.get('signature')).__name__!='str':
                return jsonify({'msg':'signature should be in text or html format'}),400

        return func(*args, **kwargs)
    return verifyBody