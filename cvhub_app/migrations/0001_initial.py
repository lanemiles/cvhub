# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('enabled', models.BooleanField()),
                ('name', models.CharField(max_length=128)),
                ('issuer', models.CharField(max_length=128)),
                ('date_awarded', models.DateField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BulletPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('enabled', models.BooleanField()),
                ('text', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=1024)),
                ('suggestion', models.CharField(max_length=1024, null=True, blank=True)),
                ('is_suggestion', models.BooleanField()),
                ('status', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ContactInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('enabled', models.BooleanField()),
                ('display_name', models.CharField(max_length=128)),
                ('phone_number', models.CharField(max_length=10)),
                ('display_email', models.CharField(max_length=128)),
                ('website', models.CharField(max_length=128)),
                ('location', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('enabled', models.BooleanField()),
                ('school', models.CharField(max_length=128)),
                ('degree_type', models.IntegerField(default=0)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('in_progress', models.BooleanField()),
                ('gpa', models.DecimalField(max_digits=3, decimal_places=2)),
                ('location', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('enabled', models.BooleanField()),
                ('title', models.CharField(max_length=128)),
                ('employer', models.CharField(max_length=128)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
                ('current', models.BooleanField()),
                ('location', models.CharField(max_length=128)),
            ],
            options={
                'ordering': ['-end_date'],
            },
        ),
        migrations.CreateModel(
            name='ResumePDF',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=512)),
                ('version_number', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('enabled', models.BooleanField()),
                ('category', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dob', models.DateField()),
                ('join_time', models.DateField()),
                ('points', models.IntegerField()),
                ('resume_url', models.CharField(max_length=512)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote_type', models.IntegerField(default=0)),
                ('comment', models.ForeignKey(to='cvhub_app.Comment')),
                ('user', models.ForeignKey(to='cvhub_app.UserInfo')),
            ],
        ),
        migrations.AddField(
            model_name='skill',
            name='owner',
            field=models.ForeignKey(to='cvhub_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='resumepdf',
            name='user',
            field=models.ForeignKey(to='cvhub_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='experience',
            name='owner',
            field=models.ForeignKey(to='cvhub_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='education',
            name='owner',
            field=models.ForeignKey(to='cvhub_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='contactinformation',
            name='owner',
            field=models.ForeignKey(to='cvhub_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(to='cvhub_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='award',
            name='owner',
            field=models.ForeignKey(to='cvhub_app.UserInfo'),
        ),
    ]
