from django.db import models
from django_enumfield import enum
import datetime

# Create your models here.


class UserInfo(models.Model):

    # our custom info
    dob = models.DateField()
    join_time = models.DateField()
    points = models.IntegerField()
    resume_url = models.CharField(max_length=512)

    # actual user authentication info
    user = models.OneToOne(User)


class CommentableResumeItem(models.Model):
    """
    Highest level abstract base class for commentable items
    """
    order = models.IntegerField()
    enabled = models.BooleanField()

    class Meta:
        abstract = True


class ResumeItem(CommentableResumeItem):
    """
    We shall see
    """

    owner = models.ForeignKey(User)

    class Meta:
        abstract = True


class BulletPoint(CommentableResumeItem):
    """
    Abstract base class for different types of resume items
    """

    text = models.CharField(max_length=1024)
    parent_item = models.ForeignKey(ResumeItem)


class ContactInformation(ResumeItem):

    display_name = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=10)
    display_email = models.CharField(max_length=128)
    website = models.CharField(max_length=128)
    location = models.CharField(max_length=128)


class DegreeType(enum.Enum):
    BA = 0
    BS = 1
    MS = 2
    MBA = 3
    PhD = 4


class Education(ResumeItem):

    school = models.CharField(max_length=128)
    degree_type = enum.EnumField(DegreeType)
    start_date = models.DateField()
    end_date = models.DateField()
    in_progress = models.BooleanField()
    gpa = models.DecimalField(max_digits=3, decimal_places=2)
    location = models.CharField(max_length=128)

    def save(self, *args, **kwargs):

        # check if in progress
        if end_date > datetime.datetime.now().date():
            in_progress = True
        else:
            in_progress = False

        super(Education, self).save(*args, **kwargs)


class Skill(ResumeItem):

    category = models.CharField(max_length=128)


class Experience(ResumeItem):

    title = models.CharField(max_length=128)
    employer = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField()

    class Meta:
        ordering = ['-end_date']

    location = models.CharField(max_length=128)


class Award(ResumeItem):

    name = models.CharField(max_length=128)
    issuer = models.CharField(max_length=128)
    date_awarded = models.DateField()


class CommentStatus(enum.Enum):
    PENDING = 0
    ACCEPTED = 1
    DECLINE = 2


class Comment(models.Model):

    author = models.ForeignKey(UserInfo)
    resume_item = models.ForeignKey(CommentableResumeItem)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=1024)
    suggestion = models.CharField(max_length=1024, null=True, blank=True)
    is_suggestion = models.BooleanField()
    status = enum.EnumField(DegreeType, default=CommentStatus.PENDING)

    class Meta:
        unique_together = ("author", "resume_item", "timestamp")

    def save(self, *args, **kwargs):

        # check if in progress
        if suggestion is not None:
            is_suggestion = True

        super(Education, self).save(*args, **kwargs)


class VoteType(enum.Enum):
    UP = 0
    DOWN = 1


class Vote(models.Model):

    user = models.ForeignKey(UserInfo)
    comment = models.ForeignKey(Comment)
    vote_type = enum.EnumField(DegreeType)

    class Meta:
        unique_together = ("user", "comment")


class ResumePDF(models.Model):

    path = models.CharField(max_length=512)
    user = models.ForeignKey(UserInfo)
    version_number = models.IntegerField()

    class Meta:
        unique_together = ("user", "version_number")
            




