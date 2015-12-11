from django.db import models
from django_enumfield import enum
import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.


class UserInfo(models.Model):

    # our custom info
    dob = models.DateField()
    points = models.IntegerField(default=0)
    user = models.OneToOneField(User, related_name='user_info')
    resume_url = models.CharField(max_length=512, null=True)
    display_name = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=10)
    website = models.CharField(max_length=128)

    education_order = models.IntegerField(default=1)
    skill_order = models.IntegerField(default=2)
    experience_order = models.IntegerField(default=3)
    award_order = models.IntegerField(default=4)

    def __unicode__(self):
        return '{} - {}'.format(self.user.username, self.dob)


class CommentableResumeItem(models.Model):
    """
    Highest level abstract base class for commentable items
    """
    order = models.IntegerField()
    enabled = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ResumeItem(CommentableResumeItem):
    """
    Superclass for Experience, Education, Skill, Award
    """

    owner = models.ForeignKey(UserInfo)

    class Meta:
        abstract = True


class BulletPoint(CommentableResumeItem):
    """
    Text that goes under a ResumeItem
    """

    text = models.CharField(max_length=1024)

    # foreign key to CommentableResumeItem
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    parent_item = GenericForeignKey('content_type', 'object_id')

    # num pending
    num_pending_comments = models.IntegerField(default=0)

    # return the parent object of the bullet point
    def get_parent(self):

        if str(self.content_type) == 'education':
            return Education.objects.get(id=self.object_id)
        elif str(self.content_type) == 'skill':
            return Skill.objects.get(id=self.object_id)
        elif str(self.content_type) == 'experience':
            return Experience.objects.get(id=self.object_id)
        elif str(self.content_type) == 'award':
            return Award.objects.get(id=self.object_id)

    def get_user_info(self):

        return self.get_parent().owner


class Education(ResumeItem):

    school = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField()
    in_progress = models.BooleanField()
    location = models.CharField(max_length=128)

    # num pending
    num_pending_comments = models.IntegerField(default=0)

    def save(self, *args, **kwargs):

        # check if in progress
        if self.end_date > datetime.datetime.now().date():
            self.in_progress = True
        else:
            self.in_progress = False

        super(Education, self).save(*args, **kwargs)


class Skill(ResumeItem):

    category = models.CharField(max_length=128)

    # num pending
    num_pending_comments = models.IntegerField(default=0)


class Experience(ResumeItem):

    title = models.CharField(max_length=128)
    employer = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField()

    # num pending
    num_pending_comments = models.IntegerField(default=0)

    class Meta:
        ordering = ['-end_date']

    location = models.CharField(max_length=128)


class Award(ResumeItem):

    name = models.CharField(max_length=128)
    issuer = models.CharField(max_length=128)
    date_awarded = models.DateField()

    # num pending
    num_pending_comments = models.IntegerField(default=0)


class CommentStatus(enum.Enum):
    PENDING = 0
    ACCEPTED = 1
    DECLINE = 2


class Comment(models.Model):

    author = models.ForeignKey(UserInfo)

    # foreign key to CommentableResumeItem
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    resume_item = GenericForeignKey('content_type', 'object_id')

    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=1024)
    suggestion = models.CharField(max_length=1024, null=True, blank=True)
    is_suggestion = models.BooleanField()
    status = enum.EnumField(CommentStatus, default=CommentStatus.PENDING)

    vote_total = models.IntegerField(default=0)

    class Meta:
        unique_together = ("author", "content_type", "object_id", "timestamp")

    # every time we save a comment, check if we have a suggestion 
    def save(self, *args, **kwargs):

        super(Comment, self).save(*args, **kwargs)

    # return the parent commental resume item of the comment
    def get_parent(self):

        if str(self.content_type) == 'education':
            return Education.objects.get(id=self.object_id)
        elif str(self.content_type) == 'skill':
            return Skill.objects.get(id=self.object_id)
        elif str(self.content_type) == 'experience':
            return Experience.objects.get(id=self.object_id)
        elif str(self.content_type) == 'award':
            return Award.objects.get(id=self.object_id)
        elif str(self.content_type) == 'bullet point':
            return BulletPoint.objects.get(id=self.object_id)

    # return the header-level parent resume item of the comment
    # that is, if the target cri is a BP, get the BP's owner
    def get_header_level_parent(self):

        if str(self.content_type) == 'education':
            return Education.objects.get(id=self.object_id)
        elif str(self.content_type) == 'skill':
            return Skill.objects.get(id=self.object_id)
        elif str(self.content_type) == 'experience':
            return Experience.objects.get(id=self.object_id)
        elif str(self.content_type) == 'award':
            return Award.objects.get(id=self.object_id)
        elif str(self.content_type) == 'bullet point':
            return BulletPoint.objects.get(id=self.object_id).get_parent()


class Section(enum.Enum):
    EDUCATION = 0
    SKILLS = 1
    AWARDS = 2
    EXPERIENCE = 3


class SectionComment(models.Model):

    author = models.ForeignKey(UserInfo, related_name='commenter')
    section_owner = models.ForeignKey(UserInfo, related_name='section_owner')
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=1024)
    status = enum.EnumField(CommentStatus, default=CommentStatus.PENDING)
    vote_total = models.IntegerField(default=0)


class VoteType(enum.Enum):
    UP = 0
    DOWN = 1


class Vote(models.Model):

    user = models.ForeignKey(UserInfo)
    comment = models.ForeignKey(Comment)
    vote_type = enum.EnumField(VoteType)

    class Meta:
        unique_together = ("user", "comment")


class ResumePDF(models.Model):

    path = models.CharField(max_length=512)
    user = models.ForeignKey(UserInfo)
    version_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ("user", "version_number")