"""
TITAN Analytics Platform - Licensing & Feature Gates
Enterprise licensing system for commercial deployments
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class LicenseTier(Enum):
    """License tier definitions"""
    COMMUNITY = 'community'
    PROFESSIONAL = 'professional'
    ENTERPRISE = 'enterprise'


@dataclass
class LicenseInfo:
    """License information container"""
    tier: LicenseTier
    organization: str
    issued_date: date
    expiry_date: Optional[date]
    max_users: int
    features: List[str]
    is_valid: bool = True
    
    def is_expired(self) -> bool:
        """Check if license has expired"""
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date
    
    def has_feature(self, feature: str) -> bool:
        """Check if license includes a feature"""
        if 'all' in self.features:
            return True
        return feature in self.features


class FeatureGate:
    """
    Feature gating system for controlling access to features
    based on license tier
    """
    
    # Feature definitions by tier
    FEATURE_MATRIX = {
        LicenseTier.COMMUNITY: {
            'basic_reports': True,
            'basic_search': True,
            'basic_templates': True,
            'pdf_export': True,
            'max_reports_month': 50,
            'max_templates': 10,
            'max_users': 5,
            'api_rate_limit': 100,
            'ai_requests_day': 20,
            # Disabled features
            'word_export': False,
            'excel_export': False,
            'anomaly_detection': False,
            'recommendation_engine': False,
            'custom_branding': False,
            'priority_support': False,
            'multi_tenant': False,
            'sso': False,
            'audit_logs': False,
            'advanced_analytics': False,
        },
        LicenseTier.PROFESSIONAL: {
            'basic_reports': True,
            'basic_search': True,
            'basic_templates': True,
            'pdf_export': True,
            'word_export': True,
            'excel_export': True,
            'max_reports_month': 500,
            'max_templates': 100,
            'max_users': 25,
            'api_rate_limit': 1000,
            'ai_requests_day': 200,
            'custom_branding': True,
            # Disabled features
            'anomaly_detection': False,
            'recommendation_engine': False,
            'priority_support': False,
            'multi_tenant': False,
            'sso': False,
            'audit_logs': False,
            'advanced_analytics': False,
        },
        LicenseTier.ENTERPRISE: {
            'basic_reports': True,
            'basic_search': True,
            'basic_templates': True,
            'pdf_export': True,
            'word_export': True,
            'excel_export': True,
            'anomaly_detection': True,
            'recommendation_engine': True,
            'custom_branding': True,
            'priority_support': True,
            'multi_tenant': True,
            'sso': True,
            'audit_logs': True,
            'advanced_analytics': True,
            'max_reports_month': 0,  # Unlimited
            'max_templates': 0,  # Unlimited
            'max_users': 0,  # Unlimited
            'api_rate_limit': 0,  # Unlimited
            'ai_requests_day': 0,  # Unlimited
        },
    }
    
    @classmethod
    def is_feature_enabled(cls, tier: LicenseTier, feature: str) -> bool:
        """Check if a feature is enabled for a license tier"""
        tier_features = cls.FEATURE_MATRIX.get(tier, cls.FEATURE_MATRIX[LicenseTier.COMMUNITY])
        return tier_features.get(feature, False)
    
    @classmethod
    def get_limit(cls, tier: LicenseTier, limit_name: str) -> int:
        """Get a numeric limit for a license tier"""
        tier_features = cls.FEATURE_MATRIX.get(tier, cls.FEATURE_MATRIX[LicenseTier.COMMUNITY])
        return tier_features.get(limit_name, 0)
    
    @classmethod
    def get_all_features(cls, tier: LicenseTier) -> Dict:
        """Get all features for a license tier"""
        return cls.FEATURE_MATRIX.get(tier, cls.FEATURE_MATRIX[LicenseTier.COMMUNITY]).copy()


class LicenseValidator:
    """
    License validation and verification
    """
    
    # Simple license key format: TITAN-TIER-ORG-HASH
    # In production, this would use proper cryptographic signing
    
    @staticmethod
    def generate_license_key(
        tier: LicenseTier,
        organization: str,
        expiry_date: Optional[date] = None
    ) -> str:
        """
        Generate a license key
        
        SECURITY NOTE: This implementation uses a simple hash-based approach
        for demonstration purposes only. For production deployments, implement:
        
        1. Asymmetric cryptographic signing (RSA/ECDSA) with private key
        2. Include expiration date in the signed payload
        3. Add hardware fingerprinting for node-locked licenses
        4. Implement license server validation for online verification
        5. Use secure storage for private keys (HSM, KMS, or Vault)
        
        Consider using established licensing libraries or services for
        enterprise-grade license management.
        """
        data = f"{tier.value}:{organization}:{expiry_date or 'perpetual'}"
        hash_value = hashlib.sha256(data.encode()).hexdigest()[:16].upper()
        tier_code = tier.value[:3].upper()
        org_code = organization[:4].upper().ljust(4, 'X')
        
        return f"TITAN-{tier_code}-{org_code}-{hash_value}"
    
    @staticmethod
    def validate_license_key(
        license_key: str,
        organization: str
    ) -> Optional[LicenseInfo]:
        """
        Validate a license key
        
        Returns LicenseInfo if valid, None otherwise
        """
        try:
            parts = license_key.split('-')
            if len(parts) != 4 or parts[0] != 'TITAN':
                logger.warning(f"Invalid license key format: {license_key}")
                return None
            
            tier_code = parts[1].lower()
            tier_map = {
                'com': LicenseTier.COMMUNITY,
                'pro': LicenseTier.PROFESSIONAL,
                'ent': LicenseTier.ENTERPRISE,
            }
            
            tier = tier_map.get(tier_code)
            if tier is None:
                logger.warning(f"Unknown license tier: {tier_code}")
                return None
            
            # Create license info
            return LicenseInfo(
                tier=tier,
                organization=organization,
                issued_date=date.today(),
                expiry_date=None,  # Would be decoded from key in production
                max_users=FeatureGate.get_limit(tier, 'max_users'),
                features=list(FeatureGate.get_all_features(tier).keys()),
                is_valid=True,
            )
            
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return None
    
    @staticmethod
    def get_community_license() -> LicenseInfo:
        """Get default community license"""
        return LicenseInfo(
            tier=LicenseTier.COMMUNITY,
            organization='Community User',
            issued_date=date.today(),
            expiry_date=None,
            max_users=5,
            features=list(FeatureGate.get_all_features(LicenseTier.COMMUNITY).keys()),
            is_valid=True,
        )


def require_feature(feature: str):
    """
    Decorator to require a specific feature
    
    Usage:
        @require_feature('anomaly_detection')
        def my_enterprise_view(request):
            ...
    """
    from functools import wraps
    from django.http import JsonResponse
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get user's license tier
            tier = LicenseTier.COMMUNITY
            if hasattr(request, 'user') and request.user.is_authenticated:
                if hasattr(request.user, 'organization') and request.user.organization:
                    tier_str = request.user.organization.license_tier
                    tier = LicenseTier(tier_str) if tier_str else LicenseTier.COMMUNITY
            
            # Check if feature is enabled
            if not FeatureGate.is_feature_enabled(tier, feature):
                return JsonResponse({
                    'error': f'Feature "{feature}" requires a higher license tier',
                    'current_tier': tier.value,
                    'required_tier': 'professional or enterprise',
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Enterprise feature list for marketing/documentation
ENTERPRISE_FEATURES = {
    'anomaly_detection': {
        'name': 'Anomaly Detection',
        'description': 'AI-powered detection of anomalies and outliers in your data',
        'tier': 'enterprise',
    },
    'recommendation_engine': {
        'name': 'Recommendation Engine',
        'description': 'Smart recommendations based on data analysis',
        'tier': 'enterprise',
    },
    'priority_support': {
        'name': 'Priority Support',
        'description': '24/7 dedicated support with SLA guarantees',
        'tier': 'enterprise',
    },
    'multi_tenant': {
        'name': 'Multi-Tenant Architecture',
        'description': 'Complete data isolation for different organizations',
        'tier': 'enterprise',
    },
    'sso': {
        'name': 'Single Sign-On (SSO)',
        'description': 'Integration with enterprise identity providers',
        'tier': 'enterprise',
    },
    'audit_logs': {
        'name': 'Audit Logging',
        'description': 'Complete audit trail for compliance requirements',
        'tier': 'enterprise',
    },
    'advanced_analytics': {
        'name': 'Advanced Analytics',
        'description': 'Advanced statistical analysis and ML models',
        'tier': 'enterprise',
    },
    'custom_branding': {
        'name': 'Custom Branding',
        'description': 'White-label the platform with your brand',
        'tier': 'professional',
    },
}
