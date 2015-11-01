# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('cvhub_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletpoint',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='bulletpoint',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together=set([('author', 'content_type', 'object_id', 'timestamp')]),
        ),
        migrations.AlterUniqueTogether(
            name='resumepdf',
            unique_together=set([('user', 'version_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'comment')]),
        ),
    ]
