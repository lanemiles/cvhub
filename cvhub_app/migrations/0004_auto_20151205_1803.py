# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0003_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='award_order',
            field=models.IntegerField(default=4),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='education_order',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='experience_order',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='skill_order',
            field=models.IntegerField(default=2),
        ),
    ]
