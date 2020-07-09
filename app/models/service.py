from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer
from app.service.services_available import services_available
           #format {"token":   , "expiry":     }

class Service(db.Document):
    """
    User Document Schema
    """

    _id = db.StringField(primary_key=True)
    serviceType = db.StringField(required=True, choices=services_available.keys())
    projectId = db.StringField(required=True)
    isActive = db.BooleanField(required=True)
    createdBy = db.StringField(required=True)
    isRemoved = db.BooleanField(required=True, default=False)   
    removedOn = db.DateTimeField(default=None, null=True)
    createdOn = db.DateTimeField(default=None, null=True, required=True)
    serviceMeta = db.DictField(default={}, required=True)

    meta = {'collection': 'services', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"srv{util.get_unique_id()}"
    
    def create(self, userObj=None, *args, **kwargs):
        self.isActive = True
        self.createdOn = util.get_current_time()
        self.isRemoved = False
        self.save()

    def save(self, *args, **kwargs):
        super(Service, self).save(*args, **kwargs)
        return self
        # return self.encode_auth_token(self.loginId)

    @staticmethod
    def get_by_id(srv_id):
        """
        Filter a service by Id.
        :param srv_id:
        :return: Service or None
        """
        return Service.objects(_id=srv_id).first()

    def remove(self):
        """
        Soft deletes the user
        """
        self.isActive = False
        self.isRemoved = True
        self.removedOn = util.get_current_time()
        self.save()

    def deactivate(self):
        """
        Deactivates service
        """
        self.isActive = False
        self.save()

    def activate(self):
        """
        Deactivates service
        """
        self.isActive = True
        self.save()