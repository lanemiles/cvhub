# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0002_bulletpoint_num_pending_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bulletpoint',
            name='num_pending_comments',
        ),
        migrations.AddField(
            model_name='resumepdf',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
