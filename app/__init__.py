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
	CORS(app, origins="https://arena.fronteous.com", expose_headers='Authorization', supports_credentials=True)
elif (os.getenv('FLASK_ENV') == 'staging'):
	config_setting = 'app.config.StagingConfig'
	CORS(app, origins="http://localhost:4200", expose_headers='Authorization', supports_credentials=True)
else:
	config_setting = 'app.config.DevelopmentConfig'
	CORS(app, origins=['localhost', 'localhost:4200'], expose_headers='Authorization', supports_credentials=True)
	
app.config.from_object(config_setting)


mail = Mail(app)

db = MongoEngine(app)

# Enabling logging
from app.logger import logger

# Healthcheck endpoint for AWS
@app.route('/', methods=['GET'])
def healthcheck():
    return "success"

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

from app.user.routes import user
app.register_blueprint(user)

from app.appointment.routes import appointment
app.register_blueprint(appointment)

from app.service.routes import service
app.register_blueprint(service)

from app.lead.routes import lead
app.register_blueprint(lead)