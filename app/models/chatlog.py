from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer
from mongoengine.queryset.visitor import Q
import re

class ChatLog(db.Document):
    """
    Chat Log Document Schema
    """

    _id = db.StringField(primary_key=True)
    conversationId = db.StringField(required=True)
    channel = db.StringField(choices=('web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram'))
    projectId = db.StringField(required=True)
    lastMessageTimestamp = db.DateTimeField(default=None, null=True)
    lastMessage = db.StringField(required=True)
    externalId = db.StringField(default="")
    chats = db.ListField(db.DictField(), default=[])
    
    meta = {'db_alias': 'fulfillment', 'collection': 'chat-logs', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(ChatLog, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"cnv_{util.get_unique_id()}"

    def save(self, *args, **kwargs):
        super(ChatLog, self).save(*args, **kwargs)
        return self
        # return self.encode_auth_token(self.loginId)

    def create(self, userObj=None, *args, **kwargs):
        self.save()


    @staticmethod
    def get_log_overview(pageNum, itemsPerPage, prj_id):
        """
        Get entire conversation for a conversation id
        """
        resObj = ChatLog.objects(projectId=prj_id).only('channel', 'externalId', 'lastMessageTimestamp', 'lastMessage').order_by('-lastMessageTimestamp').skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()
        retObj = []

        if resObj:
            for item in resObj:
                retObj.append({
                    '_id': item._id,
                    "channel": item.channel,
                    "externalId": item.externalId,
                    "lastMessage": item.lastMessage,
                    "lastMessageTimestamp": item.lastMessageTimestamp
                })
            return retObj
        else:
            return None

    
    @staticmethod
    def get_by_id(cnv_id):
        """
        Get entire conversation for a conversation id
        """
        resObj = ChatLog.objects(_id=cnv_id).first()
        retObj = {}
        if resObj:
            retObj = {
                '_id': resObj._id,
                'channel': resObj.channel,
                'externalId': resObj.externalId,
                'lastMessage': resObj.lastMessage,
                'lastMessageTimestamp': resObj.lastMessageTimestamp,
                'projectId': resObj.projectId,
                'chats': []
            }
            for item in resObj.chats:
                retObj['chats'].append({
                    "from": item.get('from'),
                    "message": item.get('message'),
                    "timestamp": item.get('timestamp'),
                    "type": item.get('type'),
                })

            return retObj
        else:
            return None 

    @staticmethod
    def get_overview_total(prj_id):
        return ChatLog.objects(projectId=prj_id).count()
 
