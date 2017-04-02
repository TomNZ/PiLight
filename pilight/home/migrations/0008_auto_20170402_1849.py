# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-02 22:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_variableparam'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transforminstance',
            name='variable_params',
        ),
        migrations.AddField(
            model_name='variableparam',
            name='param',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
