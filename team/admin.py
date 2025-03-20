from django.contrib import admin
from .models import TeamMember

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'role')

