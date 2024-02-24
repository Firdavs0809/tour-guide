# Generated by Django 4.2.9 on 2024-02-24 16:59

from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agency', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'activity',
                'verbose_name_plural': 'activities',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'booking',
                'verbose_name_plural': 'bookings',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('is_popular', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'destination',
                'verbose_name_plural': 'destinations',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('icon', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('stars', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('link', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImageUploadModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(upload_to='images/')),
            ],
        ),
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TempCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('phone_number_2', models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=30, null=True)),
                ('licence_number', models.CharField(max_length=12, unique=True)),
                ('address', models.CharField(max_length=95)),
                ('tg_username', models.CharField(blank=True, max_length=200, null=True)),
                ('website', models.CharField(blank=True, max_length=200, null=True)),
                ('is_verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterModelOptions(
            name='tourpackage',
            options={'ordering': ['-starting_date']},
        ),
        migrations.RemoveField(
            model_name='company',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='tourpackage',
            name='location',
        ),
        migrations.AddField(
            model_name='company',
            name='address',
            field=models.CharField(default='Uzbekistan', max_length=95),
        ),
        migrations.AddField(
            model_name='company',
            name='admin',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='company',
            name='chat_id',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='is_bot_connected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='company',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='company',
            name='is_waiting',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='company',
            name='licence_number',
            field=models.CharField(default='l34-3d3-3', max_length=12, unique=True),
        ),
        migrations.AddField(
            model_name='company',
            name='phone_number_2',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='company',
            name='tg_username',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='tourpackage',
            name='airport_from',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='tourpackage',
            name='airport_to',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='tourpackage',
            name='images',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.URLField(blank=True, null=True), blank=True, null=True, size=10),
        ),
        migrations.AddField(
            model_name='tourpackage',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tourpackage',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='company',
            name='average_rating',
            field=models.DecimalField(blank=True, decimal_places=1, editable=False, max_digits=3, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.CharField(default='default-agency-image.png'),
        ),
        migrations.AlterField(
            model_name='company',
            name='number_of_rating',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='company',
            name='total_rating',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='company',
            name='website',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='tourpackage',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tourpackage',
            name='image',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tourpackage',
            name='language',
            field=models.ManyToManyField(blank=True, related_name='packages', to='agency.language'),
        ),
        migrations.AlterField(
            model_name='tourpackage',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.DeleteModel(
            name='Reviews',
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cities', to='agency.country'),
        ),
        migrations.AddField(
            model_name='city',
            name='features',
            field=models.ManyToManyField(to='agency.feature'),
        ),
        migrations.AddField(
            model_name='booking',
            name='package',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='agency.tourpackage'),
        ),
    ]
