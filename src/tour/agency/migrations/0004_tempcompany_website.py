# Generated by Django 4.2.9 on 2024-02-23 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0003_alter_booking_options_booking_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tempcompany',
            name='website',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]