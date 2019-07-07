import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
	DEBUG = False
	MONGO_SSL = False

class DevelopmentConfig(BaseConfig):
	DEBUG = True
	couchURL = os.getenv('couchURL')
	couchDBName = os.getenv('couchDBName')