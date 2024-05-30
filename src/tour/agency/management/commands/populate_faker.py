import random

from django.core.management import BaseCommand
from tour.agency.models import TourPackage,City,Company
from faker import Faker


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Started database population process..."))
        faker = Faker()
        for _ in range(10000):
            TourPackage.objects.create(
                agency=Company.objects.get(id=1),
                title=faker.catch_phrase(),
                description=faker.paragraph(nb_sentences=3, variable_nb_sentences=False),
                starting_date=faker.date(),
                ending_date=faker.date(),
                price=random.randrange(340, 1000),
                airport_from=faker.city(),
                airport_to=faker.city(),
                city_from=City.objects.get_or_create(name=faker.city())[0],
                city_to=City.objects.get_or_create(name=faker.city())[0]
            )
        self.stdout.write(self.style.SUCCESS("Successfully populated the database."))
