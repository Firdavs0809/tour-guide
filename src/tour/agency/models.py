from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint
from django.utils import timezone


class Hotel(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    link = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "hotel"
        verbose_name_plural = "hotel_list"


class TempCompany(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False, )
    phone_number_2 = models.CharField(max_length=30, null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    licence_number = models.CharField(max_length=12, null=False, blank=False, unique=True)
    licence = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=95, null=False, blank=False)
    tg_username = models.CharField(max_length=200, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Company(models.Model):
    # tour agency admin
    admin = models.OneToOneField("user.User", on_delete=models.CASCADE, related_name='agency', null=True)

    # tour agency info
    name = models.CharField(max_length=200, blank=False, null=False, )
    phone_number_2 = models.CharField(max_length=30, null=True, blank=True, unique=True)
    licence_number = models.CharField(max_length=12, null=False, blank=False, unique=True, default='l34-3d3-3')
    licence = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=95, null=False, blank=False, default='Uzbekistan')

    logo = models.CharField(default="default-agency-image.png")
    website = models.CharField(max_length=200, blank=False, null=False)

    average_rating = models.DecimalField(max_digits=3, decimal_places=1, editable=False, null=True, blank=True)
    total_rating = models.IntegerField(default=0, editable=False)
    number_of_rating = models.IntegerField(default=0, editable=False)

    # tg info of agency to send notification
    tg_username = models.CharField(max_length=200, null=True, blank=True)
    chat_id = models.CharField(max_length=13, null=True, blank=True)

    is_bot_connected = models.BooleanField(default=False, )
    is_verified = models.BooleanField(default=False, )
    is_waiting = models.BooleanField(default=True, )

    def calculate_rating(self, user_rating):
        """
            Calculates the rating and modifies
             if latest changes not applied.
        """
        self.total_rating += user_rating
        self.number_of_rating += 1
        self.average_rating = round(float(self.total_rating) / float(self.number_of_rating), ndigits=2, )
        return self.save()

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=200, )

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=200, )
    is_popular = models.BooleanField(default=False)
    features = models.ManyToManyField("Feature", )
    country = models.ForeignKey(Country, related_name='cities', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self):
        return self.name


class Options(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


# Agency Tour Packages model
class TourPackage(models.Model):
    agency = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='packages')
    hotels = models.ManyToManyField(Hotel, blank=True)
    category = models.ManyToManyField(Category, blank=True)

    title = models.CharField(max_length=200, null=True, blank=True)
    image = models.CharField(null=True, blank=True)
    images = ArrayField(models.URLField(blank=True, null=True), size=10, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    language = models.ManyToManyField("Language", related_name='packages', blank=True)

    starting_date = models.DateField()
    ending_date = models.DateField()

    airport_from = models.CharField(max_length=100, null=True, blank=True)
    airport_to = models.CharField(max_length=100, null=True, blank=True)
    options = models.ManyToManyField(Options, blank=True, )

    city_from = models.ForeignKey(City, on_delete=models.CASCADE, related_name='cities_from', null=True)
    city_to = models.ForeignKey(City, on_delete=models.CASCADE, related_name='cities_to', null=True)

    number_people = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                validators=[MinValueValidator(0)])

    is_expired = models.BooleanField(default=False, )
    is_featured = models.BooleanField(default=False, )

    destinations = models.ManyToManyField("Destination", blank=True)
    activities = models.ManyToManyField('Activity', blank=True)

    def calc_expiration(self):
        if timezone.now >= self.starting_date:
            return True
        return False

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-starting_date']


# Language Model -> Different languages may be available in tour packages
class Language(models.Model):
    name = models.CharField(max_length=50, )

    def __str__(self):
        return self.name


class Destination(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "destination"
        verbose_name_plural = "destinations"
        ordering = ["name"]


class Activity(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "activity"
        verbose_name_plural = "activities"
        ordering = ["name"]


class Feature(models.Model):
    name = models.CharField(max_length=200, )
    icon = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class ImageUploadModel(models.Model):
    file = models.ImageField(null=False, blank=False, upload_to='images/')


class Booking(models.Model):
    profile = models.ForeignKey("user.Profile", on_delete=models.CASCADE, null=True)
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, null=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True)

    def __str__(self):
        return self.profile.user.phone_number + " booked " + "( " + self.package.title + " )"

    class Meta:
        verbose_name = "booking"
        verbose_name_plural = "bookings"
        ordering = ["-created_at"]
        constraints = [UniqueConstraint(
            name='Per User Per Package',
            fields=['profile', 'package']
        )]

# Review Model -> Users can give review about the company
# class Reviews(models.Model):
#     user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='reviews')
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews')
#     body = models.TextField(max_length=500, blank=True, null=True)
#     stars_given = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
#
#     def __str__(self):
#         return f"{self.user} commented {self.body[:50]}"
