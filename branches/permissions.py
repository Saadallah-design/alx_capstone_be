from rest_framework import permissions

class IsAgencyAdminOrStaff(permissions.BasePermission):
    # Global permission to check if user is agency admin or staff
    def has_permission(self,request, view):
        # must be logged in
        if not request.user or not request.user.is_authenticated:
            return False
        # must have agency admin or staff permission role
        return request.user.is_agency_admin() or request.user.is_agency_staff()


# branch owner permission
class IsBranchOwner(permissions.BasePermission):
    # this one is object level permission to check if user is owner of the branch 
    def has_object_permission(self,request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # check if the user's agency matches the branch's agency
        return obj.agency == request.user.agency