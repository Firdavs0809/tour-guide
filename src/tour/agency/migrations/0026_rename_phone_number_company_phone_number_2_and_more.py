# Generated by Django 4.2.9 on 2024-02-20 13:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agency', '0025_country_city_country'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='phone_number',
            new_name='phone_number_2',
        ),
        migrations.AddField(
            model_name='company',
            name='address',
            field=models.CharField(blank=True, max_length=95, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admins', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='company',
            name='licence_number',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]
