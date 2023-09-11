from django import forms

class Upload_excel_file(forms.Form):
    file = forms.FileField()