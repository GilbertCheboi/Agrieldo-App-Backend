from django.contrib import admin
from .models import DrugCategory, Drug, DrugOrder

admin.site.register(DrugCategory)
admin.site.register(Drug)
admin.site.register(DrugOrder)
