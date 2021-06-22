# Generated by Django 3.2.4 on 2021-06-22 10:16

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.datetime


class Migration(migrations.Migration):

    dependencies = [
        ('book2fest', '0007_merge_20210621_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.ImageField(upload_to='pictures/')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField(null=True)),
                ('date', models.DateTimeField(default=django.db.models.functions.datetime.Now())),
                ('content', models.TextField(null=True)),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='review_structure', to='book2fest.ticket')),
            ],
        ),
        migrations.AlterModelOptions(
            name='delivery',
            options={'verbose_name_plural': 'Deliveries'},
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
        migrations.AlterField(
            model_name='picture',
            name='pic',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='img', to='book2fest.pic'),
        ),
    ]