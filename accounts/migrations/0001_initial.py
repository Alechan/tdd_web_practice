# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-08-29 06:27
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('uid', models.CharField(default=uuid.uuid4, max_length=40, unique=True)),
            ],
        ),
    ]
