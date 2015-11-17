# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0003_auto_20151031_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='resume_url',
            field=models.CharField(max_length=512, null=True),
        ),
    ]
