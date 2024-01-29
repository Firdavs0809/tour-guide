from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from ..user.models import User


class Company(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    logo = models.CharField(null=True, blank=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    website = models.CharField(max_length=50, blank=False, null=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, editable=False, null=True, blank=True)
    total_rating = models.IntegerField(default=0, editable=False)
    number_of_rating = models.IntegerField(default=0, editable=False)

    def calculate_rating(self, user_rating):
        self.total_rating += user_rating
        self.number_of_rating += 1
        self.average_rating = round(float(self.total_rating) / float(self.number_of_rating), ndigits=2, )
        return self.save()

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=200,)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Agency Tour Packages model
class TourPackage(models.Model):
    agency = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='packages')

    title = models.CharField(max_length=200, null=True, blank=True)
    image = models.CharField(null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    language = models.ManyToManyField("Language", related_name='packages', )

    starting_date = models.DateField()
    ending_date = models.DateField()

    city_from = models.ForeignKey(City,on_delete=models.CASCADE,related_name='cities_from',null=True)
    city_to = models.ForeignKey(City,on_delete=models.CASCADE,related_name='cities_to',null=True)

    location = models.CharField(max_length=500, null=True, blank=True)

    number_people = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                validators=[MinValueValidator(0)])

    def __str__(self):
        return self.title


# Language Model -> Different languages may be available in tour packages
class Language(models.Model):
    name = models.CharField(max_length=50, )

    def __str__(self):
        return self.name


# Review Model -> Users can give review about the company
class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews')
    body = models.TextField(max_length=500, blank=True, null=True)
    stars_given = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"{self.user} commented {self.body[:50]}"

# class City(models.Model):
#     name = models.CharField(max_length=200)
#
#     def __str__(self):
#         return self.name