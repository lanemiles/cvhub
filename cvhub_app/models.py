from django.db import models


# Create your models here.


class CommentableResumeItem(models.Model):
    """
    Highest level abstract base class for commentable items
    """
    order = models.IntegerField()
    enabled = models.BooleanField()

    class Meta:
        abstract = True


class BulletPoint(CommentableResumeItem):
    """
    Abstract base class for different types of resume items
    """

    text = models.CharField(max_length=1024)


