from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()

class RoleBasedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            print("Permission denied: User not authenticated")
            return False

        role = request.user.user_type
        view_name = view.__class__.__name__
        print(f"has_permission: {request.method} {view_name} for user_type {role}")

        # Production Data (POST = add)
        if view_name == 'ProductionDataListCreateView' and request.method == 'POST':
            allowed = role in [User.FARMER, User.STAFF]
            print(f"ProductionData POST check: {allowed}")
            return allowed

        # Health Records (POST/PUT/PATCH = add/edit)
        if view_name in ['HealthRecordListCreateView', 'HealthRecordRetrieveUpdateView'] and request.method in ['POST', 'PUT', 'PATCH']:
            allowed = role in [User.FARMER, User.VET]
            print(f"HealthRecords {request.method} check: {allowed}")
            return allowed

        # Reproductive History (POST/PUT/PATCH = add/edit)
        if view_name in ['ReproductiveHistoryListCreateView', 'ReproductiveHistoryRetrieveUpdateView'] and request.method in ['POST', 'PUT', 'PATCH']:
            allowed = role in [User.FARMER, User.VET]
            print(f"ReproductiveHistory {request.method} check: {allowed}")
            return allowed

        # GET requests allowed for all authenticated users
        print("Default: Allowing GET or unhandled method")
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            print("Allowing GET request")
            return True

        role = request.user.user_type
        print(f"has_object_permission: {request.method} for user_type {role}, obj: {obj}, farm: {obj.animal.farm}")

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if role == User.FARMER:
                allowed = obj.animal.farm.owner == request.user
                print(f"Farmer check: Owner match = {allowed}")
                return allowed
            elif role == User.STAFF:
                allowed = obj.animal.farm.staff.filter(id=request.user.id).exists()
                print(f"Staff check: Assigned to farm = {allowed}")
                return allowed
            elif role == User.VET:
                allowed = obj.animal.farm.vets.filter(id=request.user.id).exists()
                print(f"Vet check: Assigned to farm = {allowed}")
                return allowed
        print("Default: Allowing unhandled case")
        return True
