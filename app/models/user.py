from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer

class Tokens(db.EmbeddedDocument):

    def __init__(self, arena=None, messenger=None):
        if arena:
            self.arena = arena
        if messenger:
            self.messenger = messenger

    meta = {'strict': False}
    messenger = db.DictField()          #format {"token":   , "expiry":     }
    arena = db.DictField()              #format {"token":   , "expiry":     }



class User(db.Document):
    """
    User Document Schema
    """

    _id = db.StringField(primary_key=True)
    loginType = db.StringField()
    imageUrl = db.URLField()
    email_id = db.StringField(db_field="email", required=True, unique=True)
    password = db.StringField(required=True, db_field="password")
    name = db.StringField(db_field="name")
    stats = db.DictField()
    workspaces = db.ListField(db.StringField(), default=[])             #A workspace is an organization, an email ID can be a part of one workspace only
    isActive = db.BooleanField(default=False)                           #Set to True after registering
    registeredOn = db.DateTimeField(default=None, null=True)            #When did the person actually register on the console after invite
    isRemoved = db.BooleanField(default=False)                          #Has admin removed this account or person deletes own account
    removedOn = db.DateTimeField(default=None, null=True)               #When was the account removed
    isEmailVerified = db.BooleanField(default=False)                    #If email has been verified
    # tokens = db.StringField(default=False)   #AccessTokens for console, fb messenger, etc

    meta = {'collection': 'users', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"usr{util.get_short_unique_id()}"
    
    
    def sign_up(self, userObj=None, *args, **kwargs):
        self.loginType = 'email'
        self.isActive = True
        self.registeredOn = util.get_current_time()
        self.save()

    @staticmethod
    def encode_password(password):
        return base64.b64encode(password.encode("utf-8")).decode('utf-8')

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self
        # return self.encode_auth_token(self.loginId)

    def generate_third_party_tokens(self):
        expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config.get('AUTH_TOKEN_EXPIRY_SECONDS'))
        ks = util.get_kaltura_session(self.email_id)
        self.tokens = Tokens(arena={'token':ks, 'expiry':expiry})
        self.save()

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
    def get_by_id(user_id):
        """
        Filter a user by Id.
        :param user_id:
        :return: User or None
        """
        return User.objects(_id=user_id).first()

    @staticmethod
    def get_by_email(email):
        """
        Check a user by their email address
        :param email:
        :return:
        """
        # user_list =  User.objects(email_id=email).as_pymongo()
        # if user_list:
        #     return user_list[0]
        # else:
        #     return []

        return User.objects(email_id=email).first()

    def remove(self):
        """
        Soft deletes the user
        """
        self.isRemoved = True
        self.removedOn = util.get_current_time()

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

