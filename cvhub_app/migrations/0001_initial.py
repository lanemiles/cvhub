# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('enabled', models.BooleanField(default=False)),
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
                ('enabled', models.BooleanField(default=False)),
                ('text', models.CharField(max_length=1024)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=1024)),
                ('suggestion', models.CharField(max_length=1024, null=True, blank=True)),
                ('is_suggestion', models.BooleanField()),
                ('status', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('enabled', models.BooleanField(default=False)),
                ('school', models.CharField(max_length=128)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('in_progress', models.BooleanField()),
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
                ('enabled', models.BooleanField(default=False)),
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
                ('enabled', models.BooleanField(default=False)),
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
                ('points', models.IntegerField(default=0)),
                ('resume_url', models.CharField(max_length=512, null=True)),
                ('display_name', models.CharField(max_length=128)),
                ('phone_number', models.CharField(max_length=10)),
                ('website', models.CharField(max_length=128)),
                ('education_order', models.IntegerField(default=1)),
                ('skill_order', models.IntegerField(default=2)),
                ('experience_order', models.IntegerField(default=3)),
                ('award_order', models.IntegerField(default=4)),
                ('user', models.OneToOneField(related_name='user_info', to=settings.AUTH_USER_MODEL)),
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
            model_name='comment',
            name='author',
            field=models.ForeignKey(to='cvhub_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='comment',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='award',
            name='owner',
            field=models.ForeignKey(to='cvhub_app.UserInfo'),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'comment')]),
        ),
        migrations.AlterUniqueTogether(
            name='resumepdf',
            unique_together=set([('user', 'version_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together=set([('author', 'content_type', 'object_id', 'timestamp')]),
        ),
    ]
