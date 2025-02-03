from django import forms
from .models import Message


class ImageMessageForm(forms.Form):
	image = forms.ImageField(label='')