from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsUserAuthenticatedAndAssociatedWithCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user has a one-to-one relationship with a company record
            return hasattr(request.user, 'companyprofile') 
        return False 