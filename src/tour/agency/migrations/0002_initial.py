# Generated by Django 4.2.9 on 2024-02-25 06:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agency', '0001_initial'),
        ('user', '0003_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.profile'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.UniqueConstraint(fields=('profile', 'package'), name='Per User Per Package'),
        ),
    ]
