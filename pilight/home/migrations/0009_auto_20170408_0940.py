# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-08 13:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_auto_20170402_1849'),
    ]

    operations = [
        migrations.RenameModel('Store', 'Config'),
        migrations.RenameField('Light', 'store', 'config'),
        migrations.RenameField('TransformInstance', 'store', 'config'),
        migrations.RenameField('VariableInstance', 'store', 'config'),
    ]
