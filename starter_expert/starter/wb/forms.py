from django import forms

class Upload_nmids_form(forms.Form):
    file = forms.FileField()
