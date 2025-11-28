"""
TITAN Analytics Platform - User Admin Configuration
Enterprise-ready admin for RBAC and multi-tenant management
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User, UserRole, Organization, AuditLog


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'code']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'license_tier', 'max_users', 'is_active', 'created_at']
    list_filter = ['license_tier', 'is_active']
    search_fields = ['name', 'slug']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'logo')
        }),
        ('License', {
            'fields': ('license_tier', 'license_key', 'license_expires')
        }),
        ('Limits', {
            'fields': ('max_users', 'max_reports_per_month')
        }),
        ('Settings', {
            'fields': ('settings', 'is_active'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'role', 'organization', 
        'is_verified', 'is_active', 'date_joined'
    ]
    list_filter = ['is_active', 'is_verified', 'role', 'organization']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('TITAN Profile', {
            'fields': ('role', 'organization', 'job_title', 'department', 'phone', 'avatar')
        }),
        ('Preferences', {
            'fields': ('timezone', 'language')
        }),
        ('API Access', {
            'fields': ('api_key', 'api_requests_count', 'last_api_request'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_verified', 'onboarding_completed')
        }),
    )
    
    readonly_fields = ['api_requests_count', 'last_api_request', 'created_at', 'updated_at']
    
    actions = ['generate_api_keys', 'mark_verified', 'reset_api_count']
    
    def generate_api_keys(self, request, queryset):
        for user in queryset:
            user.generate_api_key()
        self.message_user(request, f'Generated API keys for {queryset.count()} users')
    generate_api_keys.short_description = 'Generate API keys for selected users'
    
    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'Marked {queryset.count()} users as verified')
    mark_verified.short_description = 'Mark selected users as verified'
    
    def reset_api_count(self, request, queryset):
        queryset.update(api_requests_count=0)
        self.message_user(request, f'Reset API count for {queryset.count()} users')
    reset_api_count.short_description = 'Reset API request count'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'resource_type', 'resource_id', 'ip_address']
    list_filter = ['action', 'resource_type', 'timestamp']
    search_fields = ['user__username', 'resource_type', 'resource_id', 'ip_address']
    readonly_fields = ['user', 'action', 'resource_type', 'resource_id', 'details', 'ip_address', 'user_agent', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
