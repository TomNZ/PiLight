# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-01 17:22


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20170324_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='transforminstance',
            name='variable_params',
            field=models.TextField(blank=True, null=True),
        ),
    ]
