"""Builder for django table dynamic objects."""
import uuid
from typing import Any

from django.db import models, connection
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import APIException
from rest_framework.serializers import ModelSerializer

from table_builder.models import TableDefinition

symbols_to_types: dict[str, Any] = {
    'int': lambda: models.IntegerField(),
    'bool': lambda: models.BooleanField(),
    'str': lambda: models.CharField(max_length=255),
}

def get_serializer(model_class):
    class Serializer(ModelSerializer):
        class Meta:
            model = model_class
            fields = '__all__'
    return Serializer

class BuilderMappingMissingError(APIException):
    """Raise when mapping annotation type is missing."""
    status_code = 420
    default_detail = 'Builder can not create mapping, some fields may be missing.'
    default_code = '4200'


class ModelBuilder:

    def __init__(self, fields_with_annotation: dict[str, str]) -> None:
        self.fields_with_annotation = fields_with_annotation
        self.definition = None

    @property
    def field_names_to_model_fields(self) -> dict[str, Any]:
        class Meta:
            app_label = 'table_builder'
        table_fields = {'__module__': 'table_builder.models', 'Meta': Meta}
        for name, symbol in self.fields_with_annotation.items():
            try:
                table_fields[name] = symbols_to_types[symbol]()
            except (ValueError, KeyError) as e:
                raise BuilderMappingMissingError(
                    f"Missing mapping for {name}, symbol {symbol}"
                ) from e
        return table_fields

    def get_definition(self, id_):
        if not self.definition:
            self.definition = get_object_or_404(
                TableDefinition, name=self.get_table_name(id_)
            )
        return self.definition

    def generate_random_name(self):
        return self.get_table_name(uuid.uuid4())

    def get_table_name(self, id_: str) -> str:
        return f'Table{id_}'

    def build_table_model(self, table_name: str) -> models.Model:
        return type(table_name, (models.Model,), {
            **self.field_names_to_model_fields,
            'app_label': table_name,
        })

    def create_new_table(self) -> str:
        random_name = self.generate_random_name()
        table = self.build_table_model(random_name)
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(table)
        TableDefinition(
            name=random_name,
            field_names=",".join(self.fields_with_annotation.keys()),
            field_types=",".join(self.fields_with_annotation.values())
        ).save()
        return random_name.lstrip("Table")

    def alter_table(self, id_):
        new_fields = self.fields_with_annotation
        historical_table = self.build_existing_table(id_=id_)
        self.fields_with_annotation = new_fields
        table = self.build_table_model(self.get_table_name(id_))
        definition = self.definition
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(historical_table)
            schema_editor.create_model(table)
        definition.field_names = ",".join(self.fields_with_annotation.keys())
        definition.field_types = ",".join(self.fields_with_annotation.values())
        definition.save()

    def build_existing_table(self, id_) -> models.Model:
        definition = self.get_definition(id_)
        self.fields_with_annotation = dict(
            zip(definition.field_names.split(','), definition.field_types.split(','))
        )
        return self.build_table_model(definition.name)
