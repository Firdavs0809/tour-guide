# Generated by Django 4.2.9 on 2024-02-16 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesstoken',
            name='scope',
            field=models.TextField(default='*,user,admin'),
        ),
    ]