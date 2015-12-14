# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0007_sectioncomment_section_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote_type', models.IntegerField(default=0)),
                ('comment', models.ForeignKey(to='cvhub_app.SectionComment')),
                ('user', models.ForeignKey(to='cvhub_app.UserInfo')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='sectionvote',
            unique_together=set([('user', 'comment')]),
        ),
    ]
