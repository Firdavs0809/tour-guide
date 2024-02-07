# Generated by Django 4.2.9 on 2024-01-30 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0011_city_activities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='activities',
        ),
        migrations.RemoveField(
            model_name='city',
            name='destinations',
        ),
        migrations.AddField(
            model_name='tourpackage',
            name='activities',
            field=models.ManyToManyField(to='agency.activity'),
        ),
        migrations.AddField(
            model_name='tourpackage',
            name='destinations',
            field=models.ManyToManyField(to='agency.destination'),
        ),
    ]