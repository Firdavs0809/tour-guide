# Generated by Django 4.2.9 on 2024-05-30 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0011_alter_hotel_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='address_url',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
