"""
TITAN Analytics Platform - RBAC Permissions
Enterprise-grade role-based access control
"""

from rest_framework import permissions
from functools import wraps
from django.http import JsonResponse


class RBACPermission(permissions.BasePermission):
    """
    DRF permission class for role-based access control
    
    Usage in views:
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [RBACPermission]
            required_permission = 'create_reports'
    """
    
    def has_permission(self, request, view):
        # Allow anonymous access to public endpoints
        if getattr(view, 'allow_anonymous', False):
            return True
        
        # Check authentication
        if not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check for required permission
        required_permission = getattr(view, 'required_permission', None)
        if required_permission:
            return request.user.has_permission(required_permission)
        
        # Default to allow if no specific permission required
        return True
    
    def has_object_permission(self, request, view, obj):
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check for object-level permission
        object_permission = getattr(view, 'object_permission', None)
        if object_permission:
            return request.user.has_permission(object_permission)
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'author'):
            return obj.author == request.user
        
        # Check organization-level access
        if hasattr(obj, 'organization') and hasattr(request.user, 'organization'):
            if obj.organization and request.user.organization:
                return obj.organization == request.user.organization
        
        return True


class IsEnterpriseUser(permissions.BasePermission):
    """
    Check if user has enterprise license access
    """
    
    message = 'Enterprise license required for this feature'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Check organization license
        if request.user.organization:
            return request.user.organization.is_enterprise()
        
        # Check user role
        if request.user.role:
            return request.user.role.code == 'enterprise'
        
        return False


class IsOrganizationMember(permissions.BasePermission):
    """
    Check if user belongs to an organization
    """
    
    message = 'Organization membership required'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.organization is not None


class CanManageUsers(permissions.BasePermission):
    """
    Check if user can manage other users
    """
    
    message = 'User management permission required'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.has_permission('manage_users')


class CanPublishTemplates(permissions.BasePermission):
    """
    Check if user can publish templates to marketplace
    """
    
    message = 'Template publishing permission required'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.has_permission('publish_templates')


class CanAccessAPI(permissions.BasePermission):
    """
    Check if user has API access permission
    """
    
    message = 'API access not enabled for your account'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.can_access_api()


def require_permission(permission: str):
    """
    Decorator for function-based views requiring specific permission
    
    Usage:
        @require_permission('create_reports')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )
            
            if not request.user.has_permission(permission):
                return JsonResponse(
                    {'error': f'Permission denied: {permission} required'},
                    status=403
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_enterprise(view_func):
    """
    Decorator for views requiring enterprise license
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentication required'},
                status=401
            )
        
        is_enterprise = False
        if request.user.organization:
            is_enterprise = request.user.organization.is_enterprise()
        elif request.user.role:
            is_enterprise = request.user.role.code == 'enterprise'
        
        if not is_enterprise:
            return JsonResponse(
                {'error': 'Enterprise license required for this feature'},
                status=403
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper


class OrganizationFilter:
    """
    Mixin for filtering querysets by organization
    Used in multi-tenant deployments
    """
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Superusers see all
        if self.request.user.is_superuser:
            return queryset
        
        # Filter by organization if user has one
        if hasattr(self.request.user, 'organization') and self.request.user.organization:
            if hasattr(queryset.model, 'organization'):
                queryset = queryset.filter(organization=self.request.user.organization)
        
        # Filter by user if model has user field
        if hasattr(queryset.model, 'user'):
            queryset = queryset.filter(user=self.request.user)
        
        return queryset


# Permission constants for reference
PERMISSIONS = {
    'create_reports': 'Can create analytics reports',
    'view_reports': 'Can view analytics reports',
    'delete_reports': 'Can delete analytics reports',
    'manage_templates': 'Can manage all templates',
    'create_templates': 'Can create new templates',
    'access_marketplace': 'Can access template marketplace',
    'publish_templates': 'Can publish templates to marketplace',
    'manage_users': 'Can manage user accounts',
    'view_analytics': 'Can view platform analytics',
    'export_data': 'Can export data to files',
    'api_access': 'Can access REST API',
    'admin_panel': 'Can access admin panel',
    'priority_processing': 'Enterprise: Priority job processing',
    'custom_branding': 'Enterprise: Custom branding options',
    'advanced_analytics': 'Enterprise: Advanced analytics features',
    'dedicated_support': 'Enterprise: Dedicated support access',
}
