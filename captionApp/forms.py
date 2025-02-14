
from django import forms
from .models import InstaPostImage

class InstaPostImageForm(forms.ModelForm):
    image = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = InstaPostImage
        fields = ["image"]
