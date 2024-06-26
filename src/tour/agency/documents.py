from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import City, Country


@registry.register_document
class CityDocument(Document):
    class Index:
        name = "citys"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = City
        fields = [
            'name',
        ]


@registry.register_document
class CountryDocument(Document):
    class Index:
        name = "countrys"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Country
        fields = [
            'name',
        ]
