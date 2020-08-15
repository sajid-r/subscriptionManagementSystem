from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer
from mongoengine.queryset.visitor import Q
import re

class Ticket(db.Document):
    """
    Ticket Document Schema
    """

    _id = db.StringField(primary_key=True)
    externalParticipantId = db.StringField()
    notes = db.StringField(default="")
    firstName = db.StringField(required=True)
    lastName = db.StringField(default="")
    phone = db.StringField(default="")
    email = db.StringField(default="")
    channel = db.StringField(choices=('web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram'))
    projectId = db.StringField(required=True)
    category = db.ListField()
    status = db.StringField(choices=('open', 'closed', 'pending'))
    lastModified = db.DateTimeField(default=None, null=True)
    modifiedBy = db.StringField(default="")
    createdOn = db.DateTimeField(default=None, null=True)
    createdBy = db.StringField(default="")
    isDeleted = db.BooleanField(required=True, default=False)
    deletedOn = db.DateTimeField(default=None, null=True)
    deletedBy = db.StringField(default="")
    
    meta = {'db_alias': 'fulfillment', 'collection': 'tickets', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(Ticket, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"ticket_{util.get_unique_id()}"

    def save(self, *args, **kwargs):
        super(Ticket, self).save(*args, **kwargs)
        return self
        # return self.encode_auth_token(self.loginId)

    def create(self, userObj=None, *args, **kwargs):
        self.createdOn = util.get_current_time()
        self.save()

    @staticmethod
    def get_tickets(pageNum, itemsPerPage, projectId):
        objects = Ticket.objects(Q(projectId=projectId) & Q(isDeleted=False)).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()
        ticket_payload = []

        for ticket in objects:
            ticket_payload.append({
                'id':ticket._id,
                'name': ticket.firstName + " " + ticket.lastName,
                'email': ticket.email,
                'phone': ticket.phone,
                'category' : ticket.category,
                'status': ticket.status,
                'channel': ticket.channel,
                'notes': ticket.notes,
                'createdOn': ticket.createdOn,
                'modifiedBy': ticket.modifiedBy,
                'lastModified': ticket.lastModified
            })

        return ticket_payload

    @staticmethod
    def search_tickets(query, filter_obj, pageNum, itemsPerPage, projectId):
        regex = re.compile(f".*{query}.*", re.IGNORECASE)
        regex=query
        ticket_payload = []

        if query and not filter_obj:
            objects = Ticket.objects(Q(projectId=projectId) & Q(isDeleted=False) & (Q(firstName__icontains=regex) | Q(email__icontains=regex))).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()

        elif filter_obj and not query:
            #createdOn
            start = filter_obj.get('createdOn',{}).get('start', datetime.datetime(1970,1,1))
            end = filter_obj.get('createdOn',{}).get('end', datetime.datetime.now())

            #channels
            channels = filter_obj.get('channels', [])
            if channels == []:
                channels = ['web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram']

            objects = Ticket.objects(Q(projectId=projectId) & Q(isDeleted=False) & Q(createdOn__gte=start) & Q(createdOn__lte=end) & Q(channel__in=channels)).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()

        else:
            #createdOn
            start = filter_obj.get('createdOn',{}).get('start', datetime.datetime(1970,1,1))
            end = filter_obj.get('createdOn',{}).get('end', datetime.datetime.now())

            #channels
            channels = filter_obj.get('channels', [])
            if channels == []:
                channels = ['web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram']

            objects = Ticket.objects(Q(projectId=projectId) & Q(isDeleted=False) & Q(createdOn__gte=start) & Q(createdOn__lte=end) & Q(channel__in=channels) & (Q(firstName__icontains=regex) | Q(email__icontains=regex))).skip((pageNum-1)*itemsPerPage).limit(itemsPerPage).all()


        for ticket in objects:
            ticket_payload.append({
                'id':ticket._id,
                'name': ticket.firstName + " " + ticket.lastName,
                'email': ticket.email,
                'phone': ticket.phone,
                'category' : ticket.category,
                'status': ticket.status,
                'channel': ticket.channel,
                'notes': ticket.notes,
                'createdOn': ticket.createdOn,
                'modifiedBy': ticket.modifiedBy,
                'lastModified': ticket.lastModified
            })

        return ticket_payload

    @staticmethod
    def get_by_id(ticket_id):
        """
        Filter a user by Id.
        :param user_id:
        :return: User or None
        """
        return Ticket.objects(_id=ticket_id).first()

    @staticmethod
    def get_total(projectId, query="", filter_obj={}):
        """
        Get total records
        """
        if query or filter_obj:
            regex = re.compile(f".*{query}.*", re.IGNORECASE)
            regex=query

            if query and not filter_obj:
                return Ticket.objects(Q(projectId=projectId) & Q(isDeleted=False) & (Q(firstName__icontains=regex) | Q(email__icontains=regex))).count()

            elif filter_obj and not query:
                #createdOn
                start = filter_obj.get('createdOn',{}).get('start', datetime.datetime(1970,1,1))
                end = filter_obj.get('createdOn',{}).get('end', datetime.datetime.now())

                #channels
                channels = filter_obj.get('channels', [])
                if channels == []:
                    channels = ['web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram']

                return Ticket.objects(Q(projectId=projectId) & Q(isDeleted=False) & Q(createdOn__gte=start) & Q(createdOn__lte=end) & Q(channel__in=channels)).count()

            else:
                #createdOn
                start = filter_obj.get('createdOn',{}).get('start', datetime.datetime(1970,1,1))
                end = filter_obj.get('createdOn',{}).get('end', datetime.datetime.now())

                #channels
                channels = filter_obj.get('channels', [])
                if channels == []:
                    channels = ['web', 'messenger', 'phone', 'whatsapp', 'wechat', 'line', 'telegram', 'kik', 'instagram']

                return Ticket.objects(Q(projectId=projectId) & Q(isDeleted=False) & Q(createdOn__gte=start) & Q(createdOn__lte=end) & Q(channel__in=channels) & (Q(firstName__icontains=regex) | Q(email__icontains=regex))).count()
        else:
            return Ticket.objects(projectId=projectId).count()

    def delete_ticket(self, current_user):
        """
        Soft deletes the ticket
        """
        self.isDeleted = True
        self.deletedOn = util.get_current_time()
        self.deletedBy = current_user.email_id
        self.save()


    def update_ticket(self, update_obj, current_user):
        """
        Updates an ticket using the update_obj
        """
        if 'firstName' in update_obj.keys():
            self.firstName = update_obj.get('firstName')
        if 'lastName' in update_obj.keys():
            self.lastName = update_obj.get('lastName')
        if 'channel' in update_obj.keys():
            self.channel = update_obj.get('channel')
        if 'status' in update_obj.keys():
            self.status = update_obj.get('status')
        if 'notes' in update_obj.keys():
            self.notes = update_obj.get('notes')
        if 'phone' in update_obj.keys():
            self.phone = update_obj.get('phone')
        if 'email' in update_obj.keys():
            self.email = update_obj.get('email')
        if 'category' in update_obj.keys():
            self.category = update_obj.get('category')

        self.modifiedBy = current_user.email_id
        self.lastModified = util.get_current_time()

        self.save()