from django.db import models

class TableDefinition(models.Model):
    name = models.CharField()
    field_names = models.TextField()
    field_types = models.TextField()
