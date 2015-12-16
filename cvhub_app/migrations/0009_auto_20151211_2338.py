# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0008_auto_20151211_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='award_section_pending',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='education_section_pending',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='experience_section_pending',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='skills_section_pending',
            field=models.IntegerField(default=0),
        ),
    ]
