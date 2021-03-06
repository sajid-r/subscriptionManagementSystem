from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer
from mongoengine.queryset.visitor import Q
import re

class Lead(db.Document):
    """
    Lead Document Schema
    """

    _id = db.StringField(primary_key=True)
    externalParticipantId = db.StringField()
    address = db.StringField(default="")
    city = db.StringField(default="")
    country = db.StringField(default="")
    notes = db.StringField(default="")
    firstName = db.StringField(required=True)
    lastName = db.StringField(default="")
    phone = db.StringField(default="")
    email = db.StringField(default="")
    age = db.IntField()
    dateOfBirth = db.DateTimeField(default=None, null=True)
    sex = db.StringField(choices=('male', 'female', 'others'))
    channel = db.StringField(choices=('web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram'))
    projectId = db.StringField(required=True)
    lastModified = db.DateTimeField(default=None, null=True)
    modifiedBy = db.StringField(default="")
    createdOn = db.DateTimeField(default=None, null=True)
    createdBy = db.StringField(default="")
    isDeleted = db.BooleanField(default=False)
    deletedOn = db.DateTimeField(default=None, null=True)
    deletedBy = db.StringField(default="")
    
    meta = {'db_alias': 'fulfillment', 'collection': 'participants', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(Lead, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"lead_{util.get_unique_id()}"

    def save(self, *args, **kwargs):
        super(Lead, self).save(*args, **kwargs)
        return self
        # return self.encode_auth_token(self.loginId)

    def create(self, userObj=None, *args, **kwargs):
        self.createdOn = util.get_current_time()
        self.save()

    @staticmethod
    def get_leads(pageNum, itemsPerPage, projectId):
        objects = Lead.objects(Q(projectId=projectId) & Q(isDeleted=False)).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()
        lead_payload = []

        for lead in objects:
            completeName = ""
            if lead.firstName:
                completeName+=(lead.firstName+" ")
            if lead.lastName:
                completeName=lead.lastName
            lead_payload.append({
                'id':lead._id,
                'name': completeName,
                'country': lead.country,
                'address': lead.address,
                'age': lead.age,
                'dob': lead.dateOfBirth,
                'sex': lead.sex,
                'channel': lead.channel,
                'createdOn': lead.createdOn,
                'city': lead.city,
                'phone': lead.phone,
                'email': lead.email,
            })

        return lead_payload

    @staticmethod
    def search_leads(query, filter_obj, pageNum, itemsPerPage, projectId):
        regex = re.compile(f".*{query}.*", re.IGNORECASE)
        regex=query
        lead_payload = []

        if query and not filter_obj:
            objects = Lead.objects(Q(projectId=projectId) & Q(isDeleted=False) & (Q(firstName__icontains=regex) | Q(email__icontains=regex) | Q(country__icontains=regex) | Q(city__icontains=regex) | Q(address__icontains=regex))).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()

        elif filter_obj and not query:
            #createdOn
            start = filter_obj.get('createdOn',{}).get('start', datetime.datetime(1970,1,1))
            end = filter_obj.get('createdOn',{}).get('end', datetime.datetime.now())

            #channels
            channels = filter_obj.get('channels', [])
            if channels == []:
                channels = ['web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram']

            objects = Lead.objects(Q(projectId=projectId) & Q(isDeleted=False) & Q(createdOn__gte=start) & Q(createdOn__lte=end) & Q(channel__in=channels)).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()

        else:
            #createdOn
            start = filter_obj.get('createdOn',{}).get('start', datetime.datetime(1970,1,1))
            end = filter_obj.get('createdOn',{}).get('end', datetime.datetime.now())

            #channels
            channels = filter_obj.get('channels', [])
            if channels == []:
                channels = ['web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram']

            objects = Lead.objects(Q(projectId=projectId) & Q(isDeleted=False) & Q(createdOn__gte=start) & Q(createdOn__lte=end) & Q(channel__in=channels) & (Q(firstName__icontains=regex) | Q(email__icontains=regex) | Q(country__icontains=regex) | Q(city__icontains=regex) | Q(address__icontains=regex))).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()


        for lead in objects:
            lead_payload.append({
                'id':lead._id,
                'name': lead.firstName + " " + lead.lastName,
                'country': lead.country,
                'address': lead.address,
                'age': lead.age,
                'dob': lead.dateOfBirth,
                'sex': lead.sex,
                'channel': lead.channel,
                'createdOn': lead.createdOn,
                'city': lead.city,
                'phone': lead.phone,
                'email': lead.email,
            })

        return lead_payload

    @staticmethod
    def get_by_id(prj_id):
        """
        Filter a user by Id.
        :param user_id:
        :return: User or None
        """
        return Project.objects(_id=prj_id).first()

    @staticmethod
    def get_total(projectId, query="", filter_obj={}):
        """
        Get total records
        """
        if query or filter_obj:
            regex = re.compile(f".*{query}.*", re.IGNORECASE)
            regex=query

            if query and not filter_obj:
                return Lead.objects(Q(projectId=projectId) & Q(isDeleted=False) & (Q(firstName__icontains=regex) | Q(email__icontains=regex) | Q(country__icontains=regex) | Q(city__icontains=regex) | Q(address__icontains=regex))).count()

            elif filter_obj and not query:
                #createdOn
                start = filter_obj.get('createdOn',{}).get('start', datetime.datetime(1970,1,1))
                end = filter_obj.get('createdOn',{}).get('end', datetime.datetime.now())

                #channels
                channels = filter_obj.get('channels', [])
                if channels == []:
                    channels = ['web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram']

                return Lead.objects(Q(projectId=projectId) & Q(isDeleted=False) & Q(createdOn__gte=start) & Q(createdOn__lte=end) & Q(channel__in=channels)).count()

            else:
                #createdOn
                start = filter_obj.get('createdOn',{}).get('start', datetime.datetime(1970,1,1))
                end = filter_obj.get('createdOn',{}).get('end', datetime.datetime.now())

                #channels
                channels = filter_obj.get('channels', [])
                if channels == []:
                    channels = ['web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram']

                return Lead.objects(Q(projectId=projectId) & Q(isDeleted=False) & Q(createdOn__gte=start) & Q(createdOn__lte=end) & Q(channel__in=channels) & (Q(firstName__icontains=regex) | Q(email__icontains=regex) | Q(country__icontains=regex) | Q(city__icontains=regex) | Q(address__icontains=regex))).count()
        else:
            return Lead.objects(projectId=projectId).count()

    def delete_lead(self, current_user):
        """
        Soft deletes the lead
        """
        self.isDeleted = True
        self.deletedOn = util.get_current_time()
        self.deletedBy = current_user.email_id
        self.save()


    def update_lead(self, update_obj):
        """
        Updates an lead using the update_obj
        """
        if 'firstName' in update_obj.keys():
            self.firstName = update_obj.get('firstName')
        if 'lastName' in update_obj.keys():
            self.lastName = update_obj.get('lastName')
        if 'country' in update_obj.keys():
            self.country = update_obj.get('country')
        if 'address' in update_obj.keys():
            self.address = update_obj.get('address')
        if 'age' in update_obj.keys():
            self.age = update_obj.get('age')
        if 'dob' in update_obj.keys():
            self.dob = update_obj.get('dob')
        if 'sex' in update_obj.keys():
            self.sex = update_obj.get('sex')
        if 'channel' in update_obj.keys():
            self.channel = update_obj.get('channel')
        if 'city' in update_obj.keys():
            self.city = update_obj.get('city')
        if 'phone' in update_obj.keys():
            self.phone = update_obj.get('phone')
        if 'email' in update_obj.keys():
            self.email = update_obj.get('email')

        self.save()
        

