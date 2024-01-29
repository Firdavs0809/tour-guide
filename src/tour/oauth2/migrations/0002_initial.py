# Generated by Django 5.0 on 2024-01-05 05:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('oauth2', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='accesstoken',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='application',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='application',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='oauth2.application'),
        ),
        migrations.AddField(
            model_name='grant',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oauth2.application'),
        ),
        migrations.AddField(
            model_name='grant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='refreshtoken',
            name='access_token',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='refresh_token', to='oauth2.accesstoken'),
        ),
        migrations.AddField(
            model_name='refreshtoken',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oauth2.application'),
        ),
        migrations.AddField(
            model_name='refreshtoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
    ]