# Generated by Django 3.2.4 on 2021-06-16 17:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book2fest', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='event_user', to='book2fest.organizerprofile'),
        ),
    ]