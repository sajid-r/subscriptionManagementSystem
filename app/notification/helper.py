import boto3
from botocore.exceptions import ClientError
def sendingMail(recepiantmail):
    # Replace guna.hk444@gmail.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "Sender Name <guna.hk444@gmail.com>"

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
    SUBJECT = "Python Project (SDK for Python)"

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
                        'Data': BODY_HTML,
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
    else:
        response = "Email sent!"
    return(response)


def verifyEmailId(emailId):
    for emailId in body.get('emailId'):
        if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',emailId)==None:
            print('Enter valid email id')

def verifyEmailBody(func):
    def verifyBody(*args, **kwargs):
        body = request.get_json()
        print(type(body))
        print(list(body.keys()))
        if 'emailId' in list(body.keys()):
            verifyEmailId(emailId)
        else:
            print('EmailId is mondatory')
        if 'body' not in list(body.keys()):
            print('Body part is mondatory')
        if 'subject' in list(body.keys()):
            if type(body.get('subject')).__name__!='str':
                print('subject should be in text format')

        func(*args, **kwargs)
    return verifyBody