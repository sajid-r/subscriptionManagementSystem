import os
from pymongo import ReadPreference

base_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    """
    Base application configuration
    """
    DEBUG = True
    MONGODB_HOST = f'{os.getenv("MONGO_LOCAL_URI")}/{os.getenv("USERS_LOCAL_DB")}'
    MONGO_SSL = False
    USER_DB = os.getenv("USERS_DB")
    USER_COLLECTION = os.getenv("USERS_COLLECTION")
    BLACKLISTED_TOKEN_COLLECTION = os.getenv("BLACKLISTED_TOKEN_COLLECTION")
    AUTH_TOKEN_EXPIRY_SECONDS = 2592000
    SECRET_KEY = '17630c04225f4406a1e214eea732dd48'
    SECURITY_PASSWORD_SALT = '870ebbd2547e4641956b36c44270402f'
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # mail settings
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = os.getenv('APP_MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('APP_MAIL_PASSWORD')

    # mail accounts
    MAIL_DEFAULT_SENDER = 'fronteous@gmail.com'

class DevelopmentConfig(BaseConfig):
    """
    Development application configuration
    """
    AUTH_TOKEN_EXPIRY_SECONDS = 2592000
    MONGODB_HOST = f'{os.getenv("MONGO_LOCAL_URI")}/{os.getenv("USERS_LOCAL_DB")}'
    
class StagingConfig(BaseConfig):
    """
    Staging application configuration
    """
    # MONGODB_SETTINGS = [
    #     {
    #      "ALIAS": "default",
    #      "DB": os.getenv('users'),
    #      "HOST": f"{os.getenv('MONGO_LOCAL_URI')}/{os.getenv('USER_DB')}",
    #      "read_preference": ReadPreference.SECONDARY_PREFERRED,
    #     },
    #     {
    #      "ALIAS": "clean_content_db",
    #      "DB": os.getenv("CLEAN_CONTENT_DB"),
    #      "HOST": f"{os.getenv('MONGO_LOCAL_URI')}/{os.getenv('CLEAN_CONTENT_DB')}",
    #      "read_preference": ReadPreference.PRIMARY_PREFERRED,
    #     }
    # ]
    MONGODB_HOST = os.getenv("MONGO_STAGING_URI").replace('test', os.getenv("USERS_STAGING_DB"))
    AUTH_TOKEN_EXPIRY_SECONDS = 2592000
    MONGO_SSL = True


class ProductionConfig(BaseConfig):
    """
    Production application configuration
    """
    # MONGODB_SETTINGS = [
    #     {
    #      "ALIAS": "default",
    #      "DB": os.getenv('users'),
    #      "HOST": f"{os.getenv('MONGO_LOCAL_URI')}/{os.getenv('USER_DB')}",
    #      "read_preference": ReadPreference.SECONDARY_PREFERRED,
    #     },
    #     {
    #      "ALIAS": "clean_content_db",
    #      "DB": os.getenv("CLEAN_CONTENT_DB"),
    #      "HOST": f"{os.getenv('MONGO_LOCAL_URI')}/{os.getenv('CLEAN_CONTENT_DB')}",
    #      "read_preference": ReadPreference.PRIMARY_PREFERRED,
    #     }
    # ]
    MONGODB_HOST = f'{os.getenv("MONGO_PROD_URI")}'.replace('test', os.getenv("USERS_PROD_DB"))
    AUTH_TOKEN_EXPIRY_SECONDS = 2592000
    MONGO_SSL = True