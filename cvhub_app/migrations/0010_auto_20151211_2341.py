# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0009_auto_20151211_2338'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfo',
            old_name='award_section_pending',
            new_name='awards_section_pending',
        ),
    ]
