from django.db import models
from django_enumfield import enum
import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# USER INFORMATION
class UserInfo(models.Model):
    """
    Information about a user and their section ordering/comments
    """

    # user's general information
    dob = models.DateField()
    points = models.IntegerField(default=0)
    user = models.OneToOneField(User, related_name='user_info')

    # contact information
    display_name = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=10)
    website = models.CharField(max_length=128)
    resume_url = models.CharField(max_length=512, null=True)

    # order of sections
    education_order = models.IntegerField(default=1)
    skill_order = models.IntegerField(default=2)
    experience_order = models.IntegerField(default=3)
    award_order = models.IntegerField(default=4)

    # number of pending comments on each section
    education_section_pending = models.IntegerField(default=0)
    awards_section_pending = models.IntegerField(default=0)
    skills_section_pending = models.IntegerField(default=0)
    experience_section_pending = models.IntegerField(default=0)
    contact_info_pending = models.IntegerField(default=0)

    def __unicode__(self):
        return '{} - {}'.format(self.user.username, self.dob)


class ResumePDF(models.Model):
    """
    Table of links to resume PDFs
    """

    # resume owner and unique partial path to the resume PDF
    user = models.ForeignKey(UserInfo)
    path = models.CharField(max_length=512)

    # time the PDF was created
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    # the version number (relative to resume owner)
    version_number = models.IntegerField()
    class Meta:
        unique_together = ("user", "version_number")


# RESUME INFORMATION
class CommentableResumeItem(models.Model):
    """
    Highest level abstract base class for commentable items
    """

    # order relative to other header level objects in section, or
    # relative to other bullet points under one header level object
    order = models.IntegerField()

    # if True, this item is visible in the current resume version
    enabled = models.BooleanField(default=False)

    class Meta:
        abstract = True


class BulletPoint(CommentableResumeItem):
    """
    Text that goes under a ResumeItem
    """

    # bullet point text
    text = models.CharField(max_length=1024)

    # foreign key to CommentableResumeItem
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    parent_item = GenericForeignKey('content_type', 'object_id')

    # number of pending comments
    num_pending_comments = models.IntegerField(default=0)

    # resume owner
    resume_owner = models.ForeignKey(UserInfo)

    # return the parent resume item of the bullet point
    def get_parent(self):

        if str(self.content_type) == 'education':
            return Education.objects.get(id=self.object_id)
        elif str(self.content_type) == 'skill':
            return Skill.objects.get(id=self.object_id)
        elif str(self.content_type) == 'experience':
            return Experience.objects.get(id=self.object_id)
        elif str(self.content_type) == 'award':
            return Award.objects.get(id=self.object_id)

    # on save, set resume_owner to the UserInfo that owns this bullet point
    def save(self, *args, **kwargs):

        if str(self.content_type) == 'education':
            self.resume_owner = Education.objects.get(id=self.object_id).owner
        elif str(self.content_type) == 'skill':
            self.resume_owner = Skill.objects.get(id=self.object_id).owner
        elif str(self.content_type) == 'experience':
            self.resume_owner = Experience.objects.get(id=self.object_id).owner
        elif str(self.content_type) == 'award':
            self.resume_owner = Award.objects.get(id=self.object_id).owner

        super(BulletPoint, self).save(*args, **kwargs)


# HEADER-LEVEL RESUME ITEMS
class ResumeItem(CommentableResumeItem):
    """
    Superclass for Experience, Education, Skill, Award
    """

    # Resume Owner of this item
    owner = models.ForeignKey(UserInfo)

    class Meta:
        abstract = True


class Education(ResumeItem):
    """
    Education Resume Item
    """

    # school name and location
    school = models.CharField(max_length=128)
    location = models.CharField(max_length=128)

    # info about dates attended
    start_date = models.DateField()
    end_date = models.DateField()
    in_progress = models.BooleanField()

    # num pending comments
    num_pending_comments = models.IntegerField(default=0)

    # on save, dynamically set the in_progress field
    def save(self, *args, **kwargs):

        if self.end_date > datetime.datetime.now().date():
            self.in_progress = True
        else:
            self.in_progress = False

        super(Education, self).save(*args, **kwargs)


class Skill(ResumeItem):
    """
    Skill Resume Item
    """

    category = models.CharField(max_length=128)

    # num pending comments
    num_pending_comments = models.IntegerField(default=0)


class Experience(ResumeItem):
    """
    Experience Resume Item
    """

    # job title, employer, and location
    title = models.CharField(max_length=128)
    employer = models.CharField(max_length=128)
    location = models.CharField(max_length=128)

    # info about dates employed
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField()

    # num pending
    num_pending_comments = models.IntegerField(default=0)

    class Meta:
        ordering = ['-end_date']



class Award(ResumeItem):
    """
    Award Resume Item
    """

    # award name, issuer, and date awarded
    name = models.CharField(max_length=128)
    issuer = models.CharField(max_length=128)
    date_awarded = models.DateField()

    # num pending
    num_pending_comments = models.IntegerField(default=0)


# COMMENTS ON RESUME ITEMS & THEIR ASSOCIATED VOTES
class CommentStatus(enum.Enum):
    """
    Indicates the status of a comment
    """
    PENDING = 0
    ACCEPTED = 1
    DECLINE = 2


class Comment(models.Model):
    """
    A comment on a Commentable Resume Item
    """

    # comment's author and commentable resume item's owner
    author = models.ForeignKey(UserInfo, related_name="author")
    resume_owner = models.ForeignKey(UserInfo, related_name="resume_owner")

    # foreign key to CommentableResumeItem
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    resume_item = GenericForeignKey('content_type', 'object_id')

    # comment creation time, status, text, and net upvotes/downvotes
    timestamp = models.DateTimeField(auto_now_add=True)
    status = enum.EnumField(CommentStatus, default=CommentStatus.PENDING)
    text = models.CharField(max_length=1024)
    vote_total = models.IntegerField(default=0)

    # suggestion text (if applicable) and flag
    suggestion = models.CharField(max_length=1024, null=True, blank=True)
    is_suggestion = models.BooleanField()

    # enforce that no resume reviewer can comment on the same commentable
    # resume item at the exact same time - a key
    class Meta:
        unique_together = ("author", "content_type", "object_id", "timestamp")

    # every time we save a comment, check if we have a suggestion
    def save(self, *args, **kwargs):

        if str(self.content_type) == 'education':
            self.resume_owner = Education.objects.get(id=self.object_id).owner
        elif str(self.content_type) == 'skill':
            self.resume_owner = Skill.objects.get(id=self.object_id).owner
        elif str(self.content_type) == 'experience':
            self.resume_owner = Experience.objects.get(id=self.object_id).owner
        elif str(self.content_type) == 'award':
            self.resume_owner = Award.objects.get(id=self.object_id).owner
        elif str(self.content_type) == 'bullet point':
            self.resume_owner = BulletPoint.objects.get(id=self.object_id).resume_owner

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


class VoteType(enum.Enum):
    """
    Indicates upvote or downvote
    """

    UP = 0
    DOWN = 1


class Vote(models.Model):
    """
    Upvote or Downvote on a comment
    """

    # voter, the comment they're voting on, and whether it was a +1 or -1
    user = models.ForeignKey(UserInfo)
    comment = models.ForeignKey(Comment)
    vote_type = enum.EnumField(VoteType)

    # enforce that a user cannot vote more than once on a given comment
    class Meta:
        unique_together = ("user", "comment")


# SECTIONS & ASSOCIATED COMMENTS/VOTES
class SectionType(enum.Enum):
    """
    Indicates the section that a comment is on
    """
    EDUCATION = 0
    SKILLS = 1
    AWARDS = 2
    EXPERIENCE = 3
    CONTACT = 4


class SectionComment(models.Model):
    """
    Comment on a section
    """

    # comment's author and time of writing
    author = models.ForeignKey(UserInfo, related_name='commenter')
    timestamp = models.DateTimeField(auto_now_add=True)

    # the section commented on, and that section's resume owner
    section_owner = models.ForeignKey(UserInfo, related_name='section_owner')
    section_type = enum.EnumField(SectionType)

    # comment text, current status, and net upvotes/downvotes
    text = models.CharField(max_length=1024)
    status = enum.EnumField(CommentStatus, default=CommentStatus.PENDING)
    vote_total = models.IntegerField(default=0)


class SectionVote(models.Model):
    """
    Vote on a comment on a section
    """

    # voter, the section comment they're voting on, 
    # and whether it was a +1 or -1
    user = models.ForeignKey(UserInfo)
    comment = models.ForeignKey(SectionComment)
    vote_type = enum.EnumField(VoteType)

    # a user cannot vote more than once on a given section comment
    class Meta:
        unique_together = ("user", "comment")