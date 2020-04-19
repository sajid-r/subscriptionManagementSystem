import os
from pymongo import ReadPreference

base_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    """
    Base application configuration
    """
    DEBUG = True
    MONGODB_HOST = f'{os.getenv("MONGO_LOCAL_URI")}/{os.getenv("ARENA_LOCAL_DB")}'
    MONGO_SSL = False
    FULFILLMENT_DB = os.getenv("FULFILLMENT_LOCAL_DB")
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
    MONGODB_SETTINGS = [
        {
         "ALIAS": "fulfillment",
         "DB": os.getenv('FULFILLMENT_LOCAL_DB'),
         "HOST": f"{os.getenv('MONGO_LOCAL_URI')}/{os.getenv('FULFILLMENT_LOCAL_DB')}",
         "read_preference": ReadPreference.SECONDARY_PREFERRED,
        },
        {
         "ALIAS": "default",
         "DB": "cms",
         "HOST": f"{os.getenv('MONGO_LOCAL_URI')}/cms",
         "read_preference": ReadPreference.PRIMARY_PREFERRED,
        }
    ]
    AUTH_TOKEN_EXPIRY_SECONDS = 2592000
    MONGODB_HOST = f'{os.getenv("MONGO_LOCAL_URI")}/{os.getenv("ARENA_LOCAL_DB")}'
    
class StagingConfig(BaseConfig):
    """
    Staging application configuration
    """
    MONGODB_SETTINGS = [
        {
         "ALIAS": "fulfillment",
         "DB": os.getenv('FULFILLMENT_STAGING_DB'),
         "HOST": os.getenv("MONGO_STAGING_URI").replace('test', os.getenv("FULFILLMENT_STAGING_DB")),
         "read_preference": ReadPreference.SECONDARY_PREFERRED,
        },
        {
         "ALIAS": "default",
         "DB": os.getenv("ARENA_STAGING_DB"),
         "HOST": os.getenv("MONGO_STAGING_URI").replace('test', os.getenv("ARENA_STAGING_DB")),
         "read_preference": ReadPreference.PRIMARY_PREFERRED,
        }
    ]
    MONGODB_HOST = os.getenv("MONGO_STAGING_URI").replace('test', os.getenv("ARENA_STAGING_DB"))
    AUTH_TOKEN_EXPIRY_SECONDS = 2592000
    FULFILLMENT_DB = os.getenv("FULFILLMENT_STAGING_DB")
    MONGO_SSL = True


class ProductionConfig(BaseConfig):
    """
    Production application configuration
    """
    MONGODB_SETTINGS = [
        {
         "ALIAS": "fulfillment",
         "DB": os.getenv('FULFILLMENT_PROD_DB'),
         "HOST": os.getenv("MONGO_PROD_URI")}.replace('test', os.getenv("FULFILLMENT_PROD_DB")),
         "read_preference": ReadPreference.SECONDARY_PREFERRED,
        },
        {
         "ALIAS": "default",
         "DB": os.getenv("ARENA_PROD_DB"),
         "HOST": os.getenv("MONGO_PROD_URI")}.replace('test', os.getenv("ARENA_PROD_DB")),
         "read_preference": ReadPreference.PRIMARY_PREFERRED,
        }
    ]

    MONGODB_HOST = os.getenv("MONGO_PROD_URI")}.replace('test', os.getenv("ARENA_PROD_DB"))
    AUTH_TOKEN_EXPIRY_SECONDS = 2592000
    FULFILLMENT_DB = os.getenv("FULFILLMENT_PROD_DB")
    MONGO_SSL = True