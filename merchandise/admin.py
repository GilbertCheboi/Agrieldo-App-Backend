from django.contrib import admin
from .models import Merchandise
from .forms import MerchandiseForm

class MerchandiseAdmin(admin.ModelAdmin):
    form = MerchandiseForm  # Use the custom form here
    prepopulated_fields = {'slug': ('name',)}  # Prepopulate slug from name
    list_display = ('name', 'price', 'slug', 'description')
    list_filter = ('price',)
    search_fields = ('name',)

admin.site.register(Merchandise, MerchandiseAdmin)

