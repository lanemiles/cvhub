# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0010_auto_20151211_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='contact_info_pending',
            field=models.IntegerField(default=0),
        ),
    ]
