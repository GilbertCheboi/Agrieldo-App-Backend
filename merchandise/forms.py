from django import forms
from .models import Merchandise

class MerchandiseForm(forms.ModelForm):
    class Meta:
        model = Merchandise
        fields = ['name', 'slug', 'description', 'image', 'price']

    def clean_slug(self):
        # Ensure the slug is unique
        slug = self.cleaned_data['slug']
        if Merchandise.objects.filter(slug=slug).exists():
            raise forms.ValidationError("Slug must be unique.")
        return slug

