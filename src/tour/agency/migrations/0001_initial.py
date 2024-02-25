# Generated by Django 4.2.9 on 2024-02-25 06:17

from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('phone_number_2', models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ('licence_number', models.CharField(default='l34-3d3-3', max_length=12, unique=True)),
                ('address', models.CharField(default='Uzbekistan', max_length=95)),
                ('logo', models.CharField(default='default-agency-image.png')),
                ('website', models.CharField(max_length=200)),
                ('average_rating', models.DecimalField(blank=True, decimal_places=1, editable=False, max_digits=3, null=True)),
                ('total_rating', models.IntegerField(default=0, editable=False)),
                ('number_of_rating', models.IntegerField(default=0, editable=False)),
                ('tg_username', models.CharField(blank=True, max_length=200, null=True)),
                ('chat_id', models.CharField(blank=True, max_length=13, null=True)),
                ('is_bot_connected', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_waiting', models.BooleanField(default=True)),
                ('admin', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency', to=settings.AUTH_USER_MODEL)),
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
            options={
                'verbose_name': 'hotel',
                'verbose_name_plural': 'hotel_list',
            },
        ),
        migrations.CreateModel(
            name='ImageUploadModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(upload_to='images/')),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
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
        migrations.CreateModel(
            name='TourPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('image', models.CharField(blank=True, null=True)),
                ('images', django.contrib.postgres.fields.ArrayField(base_field=models.URLField(blank=True, null=True), blank=True, null=True, size=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('starting_date', models.DateField()),
                ('ending_date', models.DateField()),
                ('airport_from', models.CharField(blank=True, max_length=100, null=True)),
                ('airport_to', models.CharField(blank=True, max_length=100, null=True)),
                ('number_people', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('is_expired', models.BooleanField(default=False)),
                ('is_featured', models.BooleanField(default=False)),
                ('activities', models.ManyToManyField(blank=True, to='agency.activity')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='agency.company')),
                ('category', models.ManyToManyField(blank=True, to='agency.category')),
                ('city_from', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cities_from', to='agency.city')),
                ('city_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cities_to', to='agency.city')),
                ('destinations', models.ManyToManyField(blank=True, to='agency.destination')),
                ('language', models.ManyToManyField(blank=True, related_name='packages', to='agency.language')),
                ('options', models.ManyToManyField(blank=True, to='agency.options')),
            ],
            options={
                'ordering': ['-starting_date'],
            },
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
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('package', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='agency.tourpackage')),
            ],
            options={
                'verbose_name': 'booking',
                'verbose_name_plural': 'bookings',
                'ordering': ['-created_at'],
            },
        ),
    ]
