from django import forms
from ckeditor.widgets import CKEditorWidget

class SubscriptionForm(forms.Form):
    email = forms.EmailField()

class ContactUsForm(forms.Form):
    name = forms.CharField()
    familly_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    subject = forms.CharField()
    message_text = forms.CharField(widget=CKEditorWidget())