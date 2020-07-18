from app import app, logger, db
import datetime
import jwt
from app import helper as util
import base64
from itsdangerous import URLSafeTimedSerializer
from app.service.services_available import services_available
from app.models.service import Service
from app.models.project import Project

class Playground(db.Document):
    """
    User Document Schema
    """

    _id = db.StringField(primary_key=True)
    playgroundType = db.StringField(required=True, choices=services_available.keys())
    projectId = db.StringField(required=True)
    createdBy = db.StringField(required=True)
    createdOn = db.DateTimeField(default=None, null=True, required=True)
    lastModified = db.DateTimeField(default=None, null=True, required=True)
    isRemoved = db.BooleanField(required=True, default=False)   
    removedOn = db.DateTimeField(default=None, null=True)
    isPublished = db.BooleanField(required=True, default=False)
    publishedOn = db.DateTimeField(default=None, null=True)
    playgroundMeta = db.DictField(default={}, required=True)
    parentMarketplaceBot = db.StringField(required=True)
    publishedServiceId = db.StringField(required=True, default=None)

    meta = {'collection': 'playgrounds', 'strict': False}

    def __init__(self, *args, **kwargs):
        super(Playground, self).__init__(*args, **kwargs)
        if not self._id:
            self._id = f"play_{util.get_unique_id()}"
    
    def create(self, userObj=None, *args, **kwargs):
        self.createdOn = util.get_current_time()
        self.lastModified = util.get_current_time()
        self.isRemoved = False
        self.save()

    # def save(self, *args, **kwargs):
    #     super(Playground, self).save(*args, **kwargs)
    #     return self
        # return self.encode_auth_token(self.loginId)

    @staticmethod
    def get_by_id(srv_id):
        """
        Filter a playground by Id.
        :param srv_id:
        :return: Playground or None
        """
        return Playground.objects(_id=srv_id).first()

    @staticmethod
    def get_by_project_id(prj_id):
        """
        Get playgrounds for a project_id
        :param srv_id:
        :return: Playground or None
        """
        return Playground.objects(projectId=prj_id, isRemoved=False).all()

    @staticmethod
    def get_by_project_and_parent_bot(prj_id, parent_bot):
        """
        Get playgrounds for a project_id
        :param srv_id:
        :return: Playground or None
        """
        return Playground.objects(projectId=prj_id, isRemoved=False, parentMarketplaceBot=parent_bot).all()

    def remove(self):
        """
        Soft deletes the user
        """
        self.isRemoved = True
        self.removedOn = util.get_current_time()
        self.save()

    def publish(self, projectId, current_user):
        """
        Publish Bot - Triggers Billing
        TODO
        """
        self.publishedOn = util.get_current_time()

        if not self.isPublished:
            self.isPublished = True
            ##Create a bot service
            service = Service(serviceType='bot',
                                serviceMeta=self.playgroundMeta, 
                                projectId=projectId, 
                                createdBy=current_user.email_id)
            service.create()

            self.publishedServiceId = service._id

            #add to project
            project = Project.get_by_id(projectId)
            project.services.append(service._id)
            project.save()
        
            self.save()

        else:
            #update service
            service = Service.get_by_id(self.publishedServiceId)
            service.serviceMeta = self.playgroundMeta
            service.save()

            self.save()


        return service._id

    def update(self, updateObj):
        old_template_obj = self.playgroundMeta['template'].copy()
        for item in updateObj.keys():
            try:
                if item in old_template_obj.keys():
                    old_template_obj[item]['response'] = updateObj[item]
            except:
                pass

        self.lastModified = util.get_current_time()
        self.playgroundMeta['template'] = old_template_obj.copy()
        self.save()