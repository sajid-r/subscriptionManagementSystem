import os
from flask import Flask
from flask_cors import CORS


# Initalize application
app = Flask(__name__)

# Enabling CORS
CORS(app)

# # app configuration
# if (os.getenv('FLASK_ENV') == 'production'):
# 	config_setting = 'app.config.ProductionConfig'
# else:
# 	config_setting = 'app.config.DevelopmentConfig'
# app.config.from_object(config_setting)


from app.client.routes import client
app.register_blueprint(client)

from app.subscription.routes import subscription
app.register_blueprint(subscription)


# from app.playlist.routes import playlist

# app.register_blueprint(playlist)
