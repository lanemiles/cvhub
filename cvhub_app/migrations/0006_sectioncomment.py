# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0005_auto_20151211_0351'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=1024)),
                ('status', models.IntegerField(default=0)),
                ('vote_total', models.IntegerField(default=0)),
                ('author', models.ForeignKey(related_name='commenter', to='cvhub_app.UserInfo')),
                ('section_owner', models.ForeignKey(related_name='section_owner', to='cvhub_app.UserInfo')),
            ],
        ),
    ]
