from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer
import pytz

class Tokens(db.EmbeddedDocument):

    def __init__(self, arena=None, messenger=None):
        if arena:
            self.arena = arena
        if messenger:
            self.messenger = messenger

    meta = {'strict': False}
    messenger = db.DictField()          #format {"token":   , "expiry":     }
    arena = db.DictField()              #format {"token":   , "expiry":     }



class Project(db.Document):
    """
    User Document Schema
    """

    _id = db.StringField(primary_key=True)
    name = db.StringField(db_field="name")
    workspaceId = db.StringField(required=True)                        #A Project is an organization, an email ID can be a part of one Project only
    isActive = db.BooleanField(default=False)        #Set to True after registering
    createdBy = db.StringField(default="")           #When did the person actually register on the console after invite
    isRemoved = db.BooleanField(default=False)   
    removedOn = db.DateTimeField(default=None, null=True)           #Has admin removed this account or person deletes own account
    createdOn = db.DateTimeField(default=None, null=True)
    services = db.ListField(db.StringField(), default=[])           #When was the account removed
    timezone = db.StringField(required=True, default="UTC")

    meta = {'collection': 'projects', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"prj{util.get_short_unique_id()}"
    
    
    def create(self, userObj=None, *args, **kwargs):
        self.isActive = True
        self.createdOn = util.get_current_time()
        self.isRemoved = False
        self.save()

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        return self
        # return self.encode_auth_token(self.loginId)

    def generate_access_tokens(self):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config.get('AUTH_TOKEN_EXPIRY_SECONDS')),
            'iat': datetime.datetime.utcnow(),
            'sub': self.email_id
        }
        token = jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

        print("Token generated", token)
        return token

    def update_project(self, update_obj):
        if 'name' in update_obj.keys():
            self.name = update_obj['name']
        if 'timezone' in update_obj.keys():
            self.timezone = update_obj['timezone']
        if 'isActive' in update_obj.keys():
            self.isActive = update_obj['isActive']

        self.save()

    def get_auth_token(self):
        """
        Generates new auth token, sets auth token, returns auth token
        :param user_id: User's Id
        :return:
        """
        try:
            return self.generate_access_tokens()
        except Exception as e:
            print (e)
            app.logger.error('LOGIN', exc_info=True)
            return e

    @staticmethod
    def decode_auth_token(token):
        """
        Decoding the token to get the payload and then return the user Id in 'sub'
        :param token: Auth Token
        :return:
        """
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256', verify=False)
            is_token_blacklisted = BlackListToken.check_blacklist(token)
            if is_token_blacklisted:
                raise ValueError('Token was Blacklisted, Please login In')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise ValueError('Signature expired, Please sign in again')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid token. Please sign in again')


    @staticmethod
    def decode_verify_token(token):
        """
        Decoding the token to get the payload and then return the user Id in 'sub'
        :param token: Auth Token
        :return:
        """
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256', verify=False)
            is_token_blacklisted = BlackListToken.check_blacklist(token)
            if is_token_blacklisted:
                raise ValueError('Token was Blacklisted, Please Sign Up Again')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise ValueError('Signature expired, Please sign in again')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid token. Please sign in again')

    @staticmethod
    def get_by_id(prj_id):
        """
        Filter a user by Id.
        :param user_id:
        :return: User or None
        """
        return Project.objects(_id=prj_id).first()

    def remove(self):
        """
        Soft deletes the user
        """
        self.isRemoved = True
        self.removedOn = util.get_current_time()

    @staticmethod
    def get_timezones():
        tz_list = pytz.all_timezones
        return tz_list

class BlackListToken(db.Document):
    """
    Document to store blacklisted/invalid auth tokens
    """

    _id = db.ObjectIdField()
    token = db.StringField()
    blacklisted_on = db.StringField(default=util.get_current_time())

    meta = {'collection': app.config.get('BLACKLISTED_TOKEN_COLLECTION')}

    def __init__(self, token, *args, **kwargs):
        super(db.Document, self).__init__(*args, **kwargs)
        self.token = token
        self.blacklisted_on = util.get_current_time()

    def blacklist(self, *args, **kwargs):
        """
        Persist Blacklisted token in the database
        :return:
        """
        super(BlackListToken, self).save(*args, **kwargs)

    @staticmethod
    def check_blacklist(token):
        """
        Check to find out whether a token has already been blacklisted.
        :param token: Authorization token
        :return:
        """
        response = BlackListToken.objects(token=token).first()
        if response:
            return True
        return False