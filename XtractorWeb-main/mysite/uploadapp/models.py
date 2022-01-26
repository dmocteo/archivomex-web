from django.db import models
from django.core.validators import RegexValidator

from .validators import validate_file_extension, validate_sensivity, validate_rows, validate_columns

# Create your models here.
class Book(models.Model):
    pdf = models.FileField(upload_to='books/pdfs/', validators=[validate_file_extension], null=True, blank=False)
    page = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

class Rows(models.Model):
    rowscsv = models.CharField(null=False, blank=False, max_length=100, validators=[validate_rows])

class Sensitivity(models.Model):
    value = models.CharField(null=False, blank=False, max_length=100, validators=[validate_sensivity])

class Columns(models.Model):
    columnscsv = models.CharField(null=False, blank=False, max_length=100, validators=[validate_columns])

class SensitivityColumn(models.Model):
    value = models.CharField(null=False, blank=False, max_length=100, validators=[validate_sensivity])