# Generated by Django 4.2.9 on 2024-02-25 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tourpackage',
            old_name='hotels',
            new_name='hotel',
        ),
    ]
