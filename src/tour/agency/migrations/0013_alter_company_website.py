# Generated by Django 4.2.9 on 2024-05-30 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0012_company_address_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
    ]
