from rest_framework import permissions

class IsFarmerOrStaff(permissions.BasePermission):
    """
    Custom permission to allow only the farm owner or staff to modify production records.
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.farm.owner or request.user in obj.farm.staff.all()

