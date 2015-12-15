# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvhub_app', '0011_userinfo_contact_info_pending'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletpoint',
            name='resume_owner',
            field=models.ForeignKey(default=0, to='cvhub_app.UserInfo'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='resume_owner',
            field=models.ForeignKey(related_name='resume_owner', default=0, to='cvhub_app.UserInfo'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(related_name='author', to='cvhub_app.UserInfo'),
        ),
    ]
