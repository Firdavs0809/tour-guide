# Generated by Django 4.2.9 on 2024-02-01 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0013_features_city_features'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='features',
            field=models.ManyToManyField(to='agency.features'),
        ),
    ]