from django.contrib import admin
from .models import Farm, FarmStaff, FarmVet

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "get_staff_members", "get_vet_members", "location")
    search_fields = ("name", "owner__username", "location")
    list_filter = ("location",)

    def get_staff_members(self, obj):
        staff_list = obj.farm_staff.select_related("user").values_list("user__username", flat=True).order_by("user__username")
        return ", ".join(staff_list) if staff_list else "No staff assigned"
    get_staff_members.short_description = "Staff Members"

    def get_vet_members(self, obj):
        vet_list = obj.vet_staff.select_related("user").values_list("user__username", flat=True).order_by("user__username")
        return ", ".join(vet_list) if vet_list else "No vet assigned"
    get_vet_members.short_description = "Vets"


@admin.register(FarmStaff)
class FarmStaffAdmin(admin.ModelAdmin):
    list_display = ("user", "farm")
    search_fields = ("user__username", "farm__name")
    list_filter = ("farm",)


@admin.register(FarmVet)
class FarmVetAdmin(admin.ModelAdmin):
    list_display = ("user", "farm")
    search_fields = ("user__username", "farm__name")
    list_filter = ("farm",)

