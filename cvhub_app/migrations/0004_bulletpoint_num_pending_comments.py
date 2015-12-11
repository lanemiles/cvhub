# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0003_auto_20151210_2302'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletpoint',
            name='num_pending_comments',
            field=models.IntegerField(default=0),
        ),
    ]
