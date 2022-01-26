from django import forms

from .models import Book, Rows, Sensitivity, Columns, SensitivityColumn

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('pdf','page',)

class RowsForm(forms.ModelForm):
    class Meta:
        model = Rows
        fields = ('rowscsv',)

class SensitivityForm(forms.ModelForm):
    class Meta:
        model = Sensitivity
        fields = ('value',)

class ColumnsForm(forms.ModelForm):
    class Meta:
        model = Columns
        fields = ('columnscsv',)

class SensitivityColumnForm(forms.ModelForm):
    class Meta:
        model = SensitivityColumn
        fields = ('value',)