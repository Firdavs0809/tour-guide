from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import City


@registry.register_document
class CityDocument(Document):
    name = fields.TextField(
        attr='name',
        fields={
            'raw': fields.TextField(),
            'suggest': fields.CompletionField(),
        }
    )

    class Index:
        name = 'city'

    class Django:
        model = City
