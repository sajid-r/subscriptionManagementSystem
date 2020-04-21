from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer
from mongoengine.queryset.visitor import Q

class Appointment(db.Document):
    """
    Appointment Document Schema
    """

    _id = db.StringField(primary_key=True)
    allDay = db.BooleanField(default=False)
    appointmentType = db.StringField(default="")
    archived = db.BooleanField(default=False)
    endDate = db.DateTimeField(required=True)
    externalparticipantId = db.StringField(default="")
    lastModified = db.DateTimeField(default=None, null=True)
    location = db.StringField(default="")
    modifiedBy = db.StringField(default="")
    notes = db.StringField(default="")
    participant = db.StringField(required=True)
    participantName = db.StringField(default="")
    appointmentChannel = db.StringField(required=True)
    appointmentChannelId = db.StringField(default="")
    participantPhone = db.StringField(required=True)
    participantEmail = db.StringField(default="")
    projectId = db.StringField(required=True)
    isActive = db.BooleanField(default=True)
    isCancelled = db.BooleanField(default=False)
    cancelledOn = db.StringField(default="")
    cancelledBy = db.StringField(default="")
    provider = db.StringField(default="")
    startDate = db.DateTimeField(required=True)
    status = db.StringField(default="")

    meta = {'db_alias': app.config['FULFILLMENT_DB'], 'collection': 'appointments', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(Appointment, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"appointment_{util.get_unique_id()}"

    def save(self, *args, **kwargs):
        super(Appointment, self).save(*args, **kwargs)
        return self
        # return self.encode_auth_token(self.loginId)

    def create(self, userObj=None, *args, **kwargs):
        self.isActive = True
        self.isCancelled = False
        self.save()

    @staticmethod
    def get_appointments(start_date, end_date, projectId):
        objects = Appointment.objects(Q(startDate__gte=start_date) & Q(startDate__lte=end_date) & Q(projectId=projectId)).all()

        print("###", objects)

        app_payload = []

        for app in objects:
            app_payload.append({
                'id':app._id,
                'start': app.startDate,
                'end': app.endDate,
                'title': app.participantName,
                'phone': app.participantPhone,
                'email': app.participantEmail,
                'active': app.isActive
            })

        return app_payload

    def delete_appointment(self, current_user):
        """
        Soft deletes the appointment
        """
        self.isCancelled = True
        self.isActive = False
        self.cancelledOn = util.get_current_time()
        self.cancelledBy = current_user.email
        self.save()


    def update_appointment(self, update_obj):
        """
        Updates an appointment using the update_obj
        """
        if 'start' in update_obj.keys():
            self.startDate = update_obj.get('start')
        if 'end' in update_obj.keys():
            self.endDate = update_obj.get('end')
        if 'name' in update_obj.keys():
            self.participantName = update_obj.get('name')
        if 'phone' in update_obj.keys():
            self.participantPhone = update_obj.get('phone')
        if 'email' in update_obj.keys():
            self.participantEmail = update_obj.get('email')
        if 'provider' in update_obj.keys():
            self.provider = update_obj.get('provider')
        if 'location' in update_obj.keys():
            self.location = update_obj.get('location')

        self.save()
        

