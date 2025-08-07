from django import forms
from .models import Email
from django.contrib.auth.models import User

class EMLUploadForm(forms.Form):
    eml_file = forms.FileField()

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'from_email', 'to', 'cc', 'bcc', 'body_plain', 'body_html']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'from_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'to': forms.TextInput(attrs={'class': 'form-control'}),
            'cc': forms.TextInput(attrs={'class': 'form-control'}),
            'bcc': forms.TextInput(attrs={'class': 'form-control'}),
            'body_plain': forms.Textarea(attrs={'class': 'form-control'}),
            'body_html': forms.Textarea(attrs={'class': 'form-control'}),
        }
