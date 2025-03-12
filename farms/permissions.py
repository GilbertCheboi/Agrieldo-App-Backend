from rest_framework import permissions

class IsFarmerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only FARMER users to create farms.
    STAFF can update but not delete.
    """
    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only FARMERS can create farms
        return request.user.is_authenticated and request.user.user_type == 1

    def has_object_permission(self, request, view, obj):
        # Read-only for all safe methods
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only FARMER (Owner) can delete their farm
        if request.method == 'DELETE':
            return request.user == obj.owner
        # STAFF can update the farm details
        if request.method in ['PUT', 'PATCH']:
            return request.user in obj.staff.all() or request.user == obj.owner
        return False

