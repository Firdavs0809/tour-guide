import pandas
from django.core.management.base import BaseCommand

from tour.agency.models import Country, City


class Command(BaseCommand):
    help = "Populates the database with city and country data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Started database population process..."))
        # Populate db with city and country names
        df = pandas.read_csv('worldcities.csv')

        for index, row in df.iterrows():
            (country, created) = Country.objects.get_or_create(name=row.country)
            (city, created) = City.objects.get_or_create(name=row.city)
            city.lat = row.lat
            city.lng = row.lng
            if city not in country.cities.all():
                country.cities.add(city)

            city.save()
            country.save()

        self.stdout.write(self.style.SUCCESS("Successfully populated the database."))
