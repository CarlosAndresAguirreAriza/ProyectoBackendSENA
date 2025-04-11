from django.db.models import Model, QuerySet
from faker import Faker
from typing import Dict


fake = Faker("es_CO")


def empty_queryset(model: Model) -> QuerySet:
    """This function returns an empty queryset for the given model."""

    return model.objects.none()


def format_serializer_errors(data: Dict) -> Dict:
    """Formats error messages from Django's serializer validation failures."""

    errors_formatted = {}

    for key, value in data.items():
        if isinstance(value, list):
            errors_formatted.update({str(key): [str(error) for error in value]})
        elif isinstance(value, dict):
            data_formatted = format_serializer_errors(data=value)
            errors_formatted.update({str(key): data_formatted})

    return errors_formatted
