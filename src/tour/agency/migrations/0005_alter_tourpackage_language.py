# Generated by Django 4.2.9 on 2024-02-24 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0004_tempcompany_website'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tourpackage',
            name='language',
            field=models.ManyToManyField(blank=True, related_name='packages', to='agency.language'),
        ),
    ]
