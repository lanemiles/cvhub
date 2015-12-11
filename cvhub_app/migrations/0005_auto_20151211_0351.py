# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0004_bulletpoint_num_pending_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='award',
            name='num_pending_comments',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='education',
            name='num_pending_comments',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='experience',
            name='num_pending_comments',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='skill',
            name='num_pending_comments',
            field=models.IntegerField(default=0),
        ),
    ]
