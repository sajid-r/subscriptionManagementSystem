from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer
from mongoengine.queryset.visitor import Q
import re

class CallLog(db.Document):
    """
    Chat Log Document Schema
    """

    _id = db.StringField(primary_key=True)
    projectId = db.StringField(required=True)
    timestamp = db.DateTimeField(required=True)
    _from = db.StringField(required=True)
    to = db.StringField(required=True)
    duration = db.IntField(required=True)
    callMeta = db.DictField(default={})
    
    meta = {'db_alias': 'fulfillment', 'collection': 'call-logs', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(CallLog, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"cnv_{util.get_unique_id()}"

    def save(self, *args, **kwargs):
        super(CallLog, self).save(*args, **kwargs)
        return self
        # return self.encode_auth_token(self.loginId)

    def create(self, userObj=None, *args, **kwargs):
        self.save()


    @staticmethod
    def get_logs_overview(phone_nums, filter_obj, pageNum, itemsPerPage, projectId):
        if not phone_nums and not filter_obj:
            objects = CallLog.objects(Q(projectId=projectId)).order_by('-timestamp').skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()

        elif phone_nums and not filter_obj:
            objects = CallLog.objects(Q(projectId=projectId) & Q(_from__in=phone_nums)).order_by('-timestamp').skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()
        
        elif filter_obj and not phone_nums:
            #timestamp
            start = filter_obj.get('timestamp',{}).get('start', datetime.datetime(1970,1,1))
            end = filter_obj.get('timestamp',{}).get('end', datetime.datetime.now())

            objects = CallLog.objects(Q(projectId=projectId) & Q(timestamp__gte=start) & Q(timestamp__lte=end)).skip((pageNum-1)*itemsPerPage).order_by('-timestamp').limit(itemsPerPage).all()

        else:
            #timestamp
            start = filter_obj.get('timestamp',{}).get('start', datetime.datetime(1970,1,1))
            end = filter_obj.get('timestamp',{}).get('end', datetime.datetime.now())

            objects = CallLog.objects(Q(projectId=projectId) & Q(timestamp__gte=start) & Q(timestamp__lte=end) & Q(_from__in=phone_nums)).order_by('-timestamp').skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()

        
        log_payload = []

        for log in objects:
            log_payload.append({
                'id':log._id,
                'timestamp': log.timestamp,
                'from': log._from,
                'to': log.to,
                'duration': log.duration
            })

        return log_payload

    
    @staticmethod
    def get_by_id(_id):
        """
        Get entire log obj
        """
        resObj = CallLog.objects(_id=_id).first()
        retObj = {}
        if resObj:
            retObj = {
                'id': resObj._id,
                'timestamp': resObj.timestamp,
                'from': resObj._from,
                'to': resObj.to,
                'duration': resObj.duration
            }
            return retObj
        else:
            return None 

    @staticmethod
    def get_overview_total(phone_nums, filter_obj, prj_id):
        if not phone_nums and not filter_obj:
            return CallLog.objects(Q(projectId=prj_id)).order_by('-timestamp').count()

        if phone_nums and not filter_obj:
            return CallLog.objects(Q(projectId=prj_id) & Q(_from__in=phone_nums)).order_by('-timestamp').count()
        
        elif filter_obj and not phone_nums:
            #timestamp
            start = filter_obj.get('timestamp',{}).get('start', datetime.datetime(1970,1,1))
            end = filter_obj.get('timestamp',{}).get('end', datetime.datetime.now())

            return CallLog.objects(Q(projectId=prj_id) & Q(timestamp__gte=start) & Q(timestamp__lte=end)).order_by('-timestamp').count()

        else:
            #timestamp
            start = filter_obj.get('timestamp',{}).get('start', datetime.datetime(1970,1,1))
            end = filter_obj.get('timestamp',{}).get('end', datetime.datetime.now())

            return CallLog.objects(Q(projectId=prj_id) & Q(timestamp__gte=start) & Q(timestamp__lte=end) & Q(_from__in=phone_nums)).order_by('-timestamp').count()
 

    @staticmethod
    def get_log_search_by_phone(phone_nums, projectId):
        resObj = CallLog.objects(Q(projectId=projectId) & Q(_from__in=phone_nums)).order_by('-timestamp').order_by('-timestamp').all()
        retObj = []

        if resObj:
            for item in resObj:
                retObj.append({
                    'id': item._id,
                    'timestamp': item.timestamp,
                    'from': item._from,
                    'to': item.to,
                    'duration': item.duration
                })
            return retObj
        else:
            return None