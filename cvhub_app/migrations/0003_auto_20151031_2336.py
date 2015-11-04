# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0002_auto_20151031_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='join_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
