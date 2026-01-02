from rest_framework import permissions

class IsAgencyAdminOrStaff(permissions.BasePermission):
    """
    Allows access only to Agency Admins and Staff.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_agency_admin() or request.user.is_agency_staff()

class IsOwnerAgency(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner_agency` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner agency
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Check if the user's agency matches the object's owner_agency
        # Using the helper property 'agency' from the User model
        user_agency = request.user.agency
        
        # If user has no agency, they can't own anything
        if not user_agency:
            return False
            
        return obj.owner_agency == user_agency
