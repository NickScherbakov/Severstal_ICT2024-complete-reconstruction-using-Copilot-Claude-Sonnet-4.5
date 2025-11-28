"""
TITAN Analytics Platform - Monitoring & Logging Configuration
Enterprise-grade observability for production deployments
"""

import logging
import sys
from typing import Dict, Any
from functools import wraps
import time
import json

# Configure structured logging
class StructuredLogFormatter(logging.Formatter):
    """
    Structured JSON log formatter for production environments
    Compatible with ELK stack, Datadog, and cloud logging services
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
        
        return json.dumps(log_entry)


def configure_logging(level: str = 'INFO', json_format: bool = True) -> None:
    """
    Configure application logging
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format for structured logging
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if json_format:
        formatter = StructuredLogFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


class MetricsCollector:
    """
    Metrics collector for performance monitoring
    Can be integrated with Prometheus, Datadog, or other APM tools
    """
    
    _instance = None
    _metrics: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metrics = {
                'counters': {},
                'gauges': {},
                'histograms': {},
            }
        return cls._instance
    
    def increment(self, name: str, value: int = 1, tags: Dict = None) -> None:
        """Increment a counter metric"""
        key = self._make_key(name, tags)
        if key not in self._metrics['counters']:
            self._metrics['counters'][key] = 0
        self._metrics['counters'][key] += value
    
    def gauge(self, name: str, value: float, tags: Dict = None) -> None:
        """Set a gauge metric"""
        key = self._make_key(name, tags)
        self._metrics['gauges'][key] = value
    
    def histogram(self, name: str, value: float, tags: Dict = None) -> None:
        """Record a histogram value"""
        key = self._make_key(name, tags)
        if key not in self._metrics['histograms']:
            self._metrics['histograms'][key] = []
        self._metrics['histograms'][key].append(value)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return self._metrics.copy()
    
    def _make_key(self, name: str, tags: Dict = None) -> str:
        """Create a unique key for the metric"""
        if tags:
            tag_str = ','.join(f'{k}={v}' for k, v in sorted(tags.items()))
            return f'{name}{{{tag_str}}}'
        return name


def track_performance(metric_name: str = None):
    """
    Decorator to track function performance
    
    Usage:
        @track_performance('api.request')
        def my_api_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            collector = MetricsCollector()
            name = metric_name or f'{func.__module__}.{func.__name__}'
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                collector.increment(f'{name}.success')
                return result
            except Exception as e:
                collector.increment(f'{name}.error', tags={'exception': type(e).__name__})
                raise
            finally:
                duration = time.time() - start_time
                collector.histogram(f'{name}.duration', duration)
        
        return wrapper
    return decorator


class HealthCheck:
    """
    Health check utilities for Kubernetes probes
    """
    
    @staticmethod
    def check_database() -> bool:
        """Check database connectivity"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_rabbitmq() -> bool:
        """Check RabbitMQ connectivity"""
        try:
            from celery import current_app
            current_app.control.ping(timeout=1.0)
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_redis() -> bool:
        """Check Redis connectivity (if configured)"""
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 1)
            return cache.get('health_check') == 'ok'
        except Exception:
            return False
    
    @classmethod
    def get_health_status(cls) -> Dict[str, Any]:
        """Get comprehensive health status"""
        checks = {
            'database': cls.check_database(),
            'rabbitmq': cls.check_rabbitmq(),
        }
        
        all_healthy = all(checks.values())
        
        return {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'checks': checks,
            'timestamp': time.time(),
        }


# Prometheus metrics endpoint data
PROMETHEUS_METRICS = """
# HELP titan_requests_total Total number of requests
# TYPE titan_requests_total counter
titan_requests_total{method="GET",endpoint="/api/reports"} 0

# HELP titan_request_duration_seconds Request duration in seconds
# TYPE titan_request_duration_seconds histogram
titan_request_duration_seconds_bucket{le="0.1"} 0
titan_request_duration_seconds_bucket{le="0.5"} 0
titan_request_duration_seconds_bucket{le="1.0"} 0
titan_request_duration_seconds_bucket{le="+Inf"} 0

# HELP titan_active_users Current number of active users
# TYPE titan_active_users gauge
titan_active_users 0

# HELP titan_reports_generated_total Total reports generated
# TYPE titan_reports_generated_total counter
titan_reports_generated_total 0

# HELP titan_ai_requests_total Total AI API requests
# TYPE titan_ai_requests_total counter
titan_ai_requests_total{provider="yandexgpt"} 0
titan_ai_requests_total{provider="openai"} 0
titan_ai_requests_total{provider="anthropic"} 0
"""
