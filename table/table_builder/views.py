from django.db import models, connection
from rest_framework.views import APIView
from rest_framework.response import Response

from table_builder.builder import ModelBuilder, get_serializer


class TableBuilderView(APIView):
    def post(self, request, format=None):
        """Create new table."""
        builder = ModelBuilder(request.data)
        table_name = builder.create_new_table()
        return Response({"table_name": table_name})


    def get(self, request, format=None):
        """List all tables (not specified in requirements)."""
        tables = connection.introspection.table_names()
        db_prefix = 'table_builder_table'
        dynamic_tables = [
            table.lstrip(db_prefix) for table in tables
            if table.startswith(db_prefix) and table != f'{db_prefix}definition'
        ]
        return Response(dynamic_tables)

class TableAlteringView(APIView):
    def put(self, request, id, format=None):
        """Alter existing table."""
        builder = ModelBuilder(request.data)
        builder.alter_table(id_=id)
        return Response()

class TableRowView(APIView):
    def post(self, request, id, format=None):
        """Add a new row."""
        data = request.data
        builder = ModelBuilder({})
        table: models.Model = builder.build_existing_table(id_=id)
        serializer_class = get_serializer(table)
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class TableRowsView(APIView):
    def get(self, request, id, format=None):
        """List all rows."""
        builder = ModelBuilder({})
        table = builder.build_existing_table(id_=id)
        serializer_class = get_serializer(table)
        serializer = serializer_class(instance=table.objects.all(), many=True)
        return Response(serializer.data)
