import os
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from flask_mongoengine import MongoEngine


# Initalize application
app = Flask(__name__)

# app configuration
if (os.getenv('FLASK_ENV') == 'production'):
	config_setting = 'app.config.ProductionConfig'
else:
	config_setting = 'app.config.DevelopmentConfig'
app.config.from_object(config_setting)


mail = Mail(app)

db = MongoEngine(app)

# Enabling logging
from app.logger import logger

# Healthcheck endpoint for AWS
@app.route('/', methods=['GET'])
def healthcheck():
    return "success"

# Enabling CORS
CORS(app)

from app.notification.routes import notification
app.register_blueprint(notification)

from app.client.routes import client
app.register_blueprint(client)

from app.payment.routes import payment
app.register_blueprint(payment)

from app.auth.routes import auth
app.register_blueprint(auth)

from app.workspace.routes import workspace
app.register_blueprint(workspace)

from app.project.routes import project
app.register_blueprint(project)