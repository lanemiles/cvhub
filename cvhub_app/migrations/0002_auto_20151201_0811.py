# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='education',
            name='degree_type',
        ),
        migrations.RemoveField(
            model_name='education',
            name='gpa',
        ),
    ]
