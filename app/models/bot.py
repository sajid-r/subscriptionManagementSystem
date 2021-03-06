from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer
from app.service.services_available import services_available
from app.models.service import Service
from app.models.project import Project
from mongoengine.queryset.visitor import Q
import re

class Bot(db.Document):
    """
    Bot Document Schema
    """

    _id = db.StringField(primary_key=True)
    createdOn = db.DateTimeField(default=None, null=True, required=True)
    isRemoved = db.BooleanField(required=True, default=False)   
    removedOn = db.DateTimeField(default=None, null=True)
    isPublic = db.BooleanField(required=True, default=True)
    price = db.DecimalField(required=True)
    description = db.StringField()
    keywords = db.ListField()
    installations = db.IntField(default=0, required=True)
    overviewMediaUrl = db.StringField()
    overviewRichText = db.StringField()
    marketplaceCardMediaUrl = db.StringField()
    tags = db.ListField()
    name = db.StringField()
    botMeta = db.DictField(default={}, required=True)

    meta = {'collection': 'bots', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"bot_{util.get_unique_id()}"
    
    def create(self, userObj=None, *args, **kwargs):
        self.createdOn = util.get_current_time()
        self.isRemoved = False
        self.save()

    def save(self, *args, **kwargs):
        super(Bot, self).save(*args, **kwargs)
        return self
        # return self.encode_auth_token(self.loginId)

    @staticmethod
    def get_by_id(bot_id):
        """
        Filter a playground by Id.
        :param srv_id:
        :return: Bot or None
        """
        return Bot.objects(_id=bot_id).first()

    @staticmethod
    def get_by_id_no_template(bot_id):
        """
        Filter a playground by Id.
        :param srv_id:
        :return: Bot or None
        """
        return Bot.objects(_id=bot_id).exclude("botMeta.template").first()

    def remove(self):
        """
        Soft deletes the user
        """
        self.isRemoved = True
        self.removedOn = util.get_current_time()
        self.save()

    @staticmethod
    def get_catalog(filterObj):
        if filterObj:
            return Bot.objects(Q(isPublic=True) & Q(isRemoved=False) & Q(tags__contains=filterObj)).only('_id', 'description', 'price', 'marketplaceCardMediaUrl', 'name', 'tags').all()
        else:
            return Bot.objects(Q(isPublic=True) & Q(isRemoved=False)).only('_id', 'description', 'price', 'marketplaceCardMediaUrl', 'name', 'tags').all()

    @staticmethod
    def get_tags(filterObj):
        res = Bot.objects(Q(isPublic=True) & Q(isRemoved=False)).only('tags').all()
        payload = []
        for item in res:
            payload.extend(item.tags)

        return payload

    @staticmethod
    def search_bots(query, filter_obj, pageNum, itemsPerPage, projectId):
        regex = re.compile(f".*{query}.*", re.IGNORECASE)
        regex=query
        bot_payload = []

        if query and not filter_obj:
            objects = Bot.objects(Q(isRemoved=False) & Q(keywords__icontains=regex)).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).only('_id', 'description', 'price', 'marketplaceCardMediaUrl', 'name', 'tags').all()

        elif filter_obj and not query:
            objects = Bot.get_catalog(filter_obj)

        else:
            objects = Bot.objects(Q(isPublic=True) & Q(isRemoved=False) & Q(tags__contains=filter_obj) & Q(keywords__icontains=regex)).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).only('_id', 'description', 'price', 'marketplaceCardMediaUrl', 'name', 'tags').all()


        return objects