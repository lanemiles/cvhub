# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0004_auto_20151031_2340'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='join_time',
        ),
    ]
