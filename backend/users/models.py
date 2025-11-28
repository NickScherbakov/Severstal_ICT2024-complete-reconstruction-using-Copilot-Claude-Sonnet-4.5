"""
TITAN Analytics Platform - User Model with RBAC
Enterprise-ready role-based access control system
"""

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserRole(models.Model):
    """
    Role definitions for RBAC
    Supports hierarchical permissions for enterprise deployments
    """
    # Built-in roles
    ADMIN = 'admin'
    ANALYST = 'analyst'
    VIEWER = 'viewer'
    ENTERPRISE = 'enterprise'
    
    ROLE_CHOICES = (
        (ADMIN, 'Administrator'),
        (ANALYST, 'Analyst'),
        (VIEWER, 'Viewer'),
        (ENTERPRISE, 'Enterprise User'),
    )
    
    name = models.CharField(
        'Role Name',
        max_length=50,
        unique=True
    )
    code = models.CharField(
        'Role Code',
        max_length=30,
        choices=ROLE_CHOICES,
        unique=True
    )
    description = models.TextField(
        'Description',
        blank=True
    )
    permissions = models.JSONField(
        'Permissions',
        default=dict,
        help_text='JSON object defining role permissions'
    )
    is_active = models.BooleanField(
        'Active',
        default=True
    )
    created_at = models.DateTimeField(
        'Created At',
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission"""
        if self.code == self.ADMIN:
            return True  # Admin has all permissions
        return self.permissions.get(permission, False)
    
    @classmethod
    def get_default_permissions(cls, role_code: str) -> dict:
        """Get default permissions for a role"""
        permissions_map = {
            cls.ADMIN: {
                'create_reports': True,
                'view_reports': True,
                'delete_reports': True,
                'manage_templates': True,
                'create_templates': True,
                'access_marketplace': True,
                'publish_templates': True,
                'manage_users': True,
                'view_analytics': True,
                'export_data': True,
                'api_access': True,
                'admin_panel': True,
            },
            cls.ANALYST: {
                'create_reports': True,
                'view_reports': True,
                'delete_reports': True,
                'manage_templates': False,
                'create_templates': True,
                'access_marketplace': True,
                'publish_templates': False,
                'manage_users': False,
                'view_analytics': True,
                'export_data': True,
                'api_access': True,
                'admin_panel': False,
            },
            cls.VIEWER: {
                'create_reports': False,
                'view_reports': True,
                'delete_reports': False,
                'manage_templates': False,
                'create_templates': False,
                'access_marketplace': True,
                'publish_templates': False,
                'manage_users': False,
                'view_analytics': True,
                'export_data': False,
                'api_access': False,
                'admin_panel': False,
            },
            cls.ENTERPRISE: {
                'create_reports': True,
                'view_reports': True,
                'delete_reports': True,
                'manage_templates': True,
                'create_templates': True,
                'access_marketplace': True,
                'publish_templates': True,
                'manage_users': False,
                'view_analytics': True,
                'export_data': True,
                'api_access': True,
                'admin_panel': False,
                # Enterprise-specific features
                'priority_processing': True,
                'custom_branding': True,
                'advanced_analytics': True,
                'dedicated_support': True,
            },
        }
        return permissions_map.get(role_code, {})


class Organization(models.Model):
    """
    Organization/Tenant model for multi-tenant support
    Enables enterprise deployments with isolated data
    """
    # License tiers
    COMMUNITY = 'community'
    PROFESSIONAL = 'professional'
    ENTERPRISE = 'enterprise'
    
    LICENSE_TIERS = (
        (COMMUNITY, 'Community (Free)'),
        (PROFESSIONAL, 'Professional'),
        (ENTERPRISE, 'Enterprise'),
    )
    
    name = models.CharField(
        'Organization Name',
        max_length=200
    )
    slug = models.SlugField(
        'Slug',
        unique=True
    )
    description = models.TextField(
        'Description',
        blank=True
    )
    logo = models.ImageField(
        'Logo',
        upload_to='organizations/',
        blank=True,
        null=True
    )
    license_tier = models.CharField(
        'License Tier',
        max_length=20,
        choices=LICENSE_TIERS,
        default=COMMUNITY
    )
    license_key = models.CharField(
        'License Key',
        max_length=100,
        blank=True
    )
    license_expires = models.DateField(
        'License Expiration',
        blank=True,
        null=True
    )
    settings = models.JSONField(
        'Settings',
        default=dict,
        blank=True
    )
    max_users = models.PositiveIntegerField(
        'Max Users',
        default=5,
        help_text='Maximum number of users allowed (0 = unlimited)'
    )
    max_reports_per_month = models.PositiveIntegerField(
        'Max Reports Per Month',
        default=100,
        help_text='Maximum reports per month (0 = unlimited)'
    )
    is_active = models.BooleanField(
        'Active',
        default=True
    )
    created_at = models.DateTimeField(
        'Created At',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Updated At',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
    
    def __str__(self) -> str:
        return self.name
    
    def is_enterprise(self) -> bool:
        """Check if organization has enterprise license"""
        return self.license_tier == self.ENTERPRISE
    
    def get_feature_limits(self) -> dict:
        """Get feature limits based on license tier"""
        limits = {
            self.COMMUNITY: {
                'max_users': 5,
                'max_reports_per_month': 50,
                'max_templates': 10,
                'api_rate_limit': 100,  # requests per hour
                'export_formats': ['pdf'],
                'ai_requests_per_day': 20,
                'custom_branding': False,
                'priority_support': False,
            },
            self.PROFESSIONAL: {
                'max_users': 25,
                'max_reports_per_month': 500,
                'max_templates': 100,
                'api_rate_limit': 1000,
                'export_formats': ['pdf', 'word', 'excel'],
                'ai_requests_per_day': 200,
                'custom_branding': True,
                'priority_support': False,
            },
            self.ENTERPRISE: {
                'max_users': 0,  # Unlimited
                'max_reports_per_month': 0,  # Unlimited
                'max_templates': 0,  # Unlimited
                'api_rate_limit': 0,  # Unlimited
                'export_formats': ['pdf', 'word', 'excel', 'json', 'csv'],
                'ai_requests_per_day': 0,  # Unlimited
                'custom_branding': True,
                'priority_support': True,
            },
        }
        return limits.get(self.license_tier, limits[self.COMMUNITY])


class User(AbstractUser):
    """
    Extended User model with RBAC and multi-tenant support
    """
    role = models.ForeignKey(
        UserRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Role'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Organization'
    )
    job_title = models.CharField(
        'Job Title',
        max_length=100,
        blank=True
    )
    department = models.CharField(
        'Department',
        max_length=100,
        blank=True
    )
    phone = models.CharField(
        'Phone',
        max_length=20,
        blank=True
    )
    avatar = models.ImageField(
        'Avatar',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    timezone = models.CharField(
        'Timezone',
        max_length=50,
        default='UTC'
    )
    language = models.CharField(
        'Language',
        max_length=10,
        default='ru',
        choices=(
            ('ru', 'Русский'),
            ('en', 'English'),
        )
    )
    api_key = models.CharField(
        'API Key',
        max_length=100,
        blank=True,
        unique=True,
        null=True,
        help_text='Personal API key for programmatic access'
    )
    api_requests_count = models.PositiveIntegerField(
        'API Requests Count',
        default=0
    )
    last_api_request = models.DateTimeField(
        'Last API Request',
        blank=True,
        null=True
    )
    is_verified = models.BooleanField(
        'Email Verified',
        default=False
    )
    onboarding_completed = models.BooleanField(
        'Onboarding Completed',
        default=False
    )
    created_at = models.DateTimeField(
        'Created At',
        auto_now_add=True,
        null=True
    )
    updated_at = models.DateTimeField(
        'Updated At',
        auto_now=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.is_superuser:
            return True
        if self.role:
            return self.role.has_permission(permission)
        return False
    
    def get_organization_limits(self) -> dict:
        """Get feature limits from user's organization"""
        if self.organization:
            return self.organization.get_feature_limits()
        # Default to community limits
        return Organization().get_feature_limits()
    
    def can_create_report(self) -> bool:
        """Check if user can create reports"""
        return self.has_permission('create_reports')
    
    def can_access_api(self) -> bool:
        """Check if user has API access"""
        return self.has_permission('api_access')
    
    def generate_api_key(self) -> str:
        """Generate a new API key for the user"""
        import secrets
        self.api_key = f"titan_{secrets.token_urlsafe(32)}"
        self.save(update_fields=['api_key'])
        return self.api_key


class AuditLog(models.Model):
    """
    Audit log for tracking user actions
    Important for enterprise compliance and security
    """
    ACTION_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('api_call', 'API Call'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='User'
    )
    action = models.CharField(
        'Action',
        max_length=20,
        choices=ACTION_TYPES
    )
    resource_type = models.CharField(
        'Resource Type',
        max_length=100
    )
    resource_id = models.CharField(
        'Resource ID',
        max_length=100,
        blank=True
    )
    details = models.JSONField(
        'Details',
        default=dict,
        blank=True
    )
    ip_address = models.GenericIPAddressField(
        'IP Address',
        blank=True,
        null=True
    )
    user_agent = models.TextField(
        'User Agent',
        blank=True
    )
    timestamp = models.DateTimeField(
        'Timestamp',
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self) -> str:
        return f"{self.user} - {self.action} - {self.resource_type}"