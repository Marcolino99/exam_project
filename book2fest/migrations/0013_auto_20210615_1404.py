# Generated by Django 3.1.7 on 2021-06-15 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book2fest', '0012_auto_20210615_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='path',
            field=models.FilePathField(default='static/images/default.png', path='static/images/icon'),
        ),
    ]
