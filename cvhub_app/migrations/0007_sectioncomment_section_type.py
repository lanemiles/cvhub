# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0006_sectioncomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectioncomment',
            name='section_type',
            field=models.IntegerField(default=0),
        ),
    ]
