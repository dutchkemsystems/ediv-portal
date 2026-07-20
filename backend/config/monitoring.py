"""
Performance monitoring utilities for Education District IV Portal.
"""

import time
import logging
from functools import wraps
from django.db import connection
from django.core.cache import cache

logger = logging.getLogger('performance')


def monitor_queries(func):
    """Decorator to monitor database queries."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Reset query count
        initial_queries = len(connection.queries)
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        # Calculate metrics
        end_time = time.time()
        query_count = len(connection.queries) - initial_queries
        execution_time = end_time - start_time
        
        # Log if slow
        if execution_time > 1.0 or query_count > 10:
            logger.warning(
                f"Slow query detected in {func.__name__}: "
                f"{query_count} queries in {execution_time:.2f}s"
            )
        
        return result
    return wrapper


def monitor_api_performance(func):
    """Decorator to monitor API performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_queries = len(connection.queries)
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        query_count = len(connection.queries) - start_queries
        execution_time = end_time - start_time
        
        # Store metrics in cache
        cache_key = f"ediv:api_metrics:{func.__name__}"
        metrics = cache.get(cache_key, {
            'total_calls': 0,
            'total_time': 0,
            'total_queries': 0,
            'avg_time': 0,
            'avg_queries': 0,
        })
        
        metrics['total_calls'] += 1
        metrics['total_time'] += execution_time
        metrics['total_queries'] += query_count
        metrics['avg_time'] = metrics['total_time'] / metrics['total_calls']
        metrics['avg_queries'] = metrics['total_queries'] / metrics['total_calls']
        
        cache.set(cache_key, metrics, timeout=3600)
        
        return result
    return wrapper


class PerformanceMetrics:
    """Performance metrics collection and reporting."""
    
    @staticmethod
    def get_api_metrics():
        """Get API performance metrics."""
        from django.core.cache import cache
        
        metrics = {}
        api_endpoints = [
            'schools', 'staff', 'students', 'academics',
            'attendance', 'finance', 'files', 'workflows'
        ]
        
        for endpoint in api_endpoints:
            cache_key = f"ediv:api_metrics:{endpoint}"
            endpoint_metrics = cache.get(cache_key)
            if endpoint_metrics:
                metrics[endpoint] = endpoint_metrics
        
        return metrics
    
    @staticmethod
    def get_database_metrics():
        """Get database performance metrics."""
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Get table sizes
            cursor.execute("""
                SELECT 
                    relname as table_name,
                    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
                    pg_size_pretty(pg_relation_size(relid)) as table_size,
                    pg_size_pretty(pg_indexes_size(relid)) as index_size
                FROM pg_catalog.pg_statio_user_tables
                ORDER BY pg_total_relation_size(relid) DESC
                LIMIT 20;
            """)
            
            tables = cursor.fetchall()
            
            # Get index usage
            cursor.execute("""
                SELECT 
                    indexrelname as index_name,
                    idx_scan as times_used,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
                LIMIT 20;
            """)
            
            indexes = cursor.fetchall()
        
        return {
            'tables': tables,
            'indexes': indexes
        }
    
    @staticmethod
    def get_cache_metrics():
        """Get cache performance metrics."""
        from django.core.cache import cache
        
        try:
            from redis import Redis
            redis_client = Redis.from_url(cache._server)
            info = redis_client.info()
            
            return {
                'hit_rate': info.get('keyspace_hits', 0) / (
                    info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)
                ) * 100,
                'total_keys': info.get('db0', {}).get('keys', 0),
                'memory_used': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
            }
        except Exception:
            return {
                'hit_rate': 0,
                'total_keys': 0,
                'memory_used': 'N/A',
                'connected_clients': 0,
            }
    
    @staticmethod
    def generate_report():
        """Generate comprehensive performance report."""
        return {
            'api_metrics': PerformanceMetrics.get_api_metrics(),
            'database_metrics': PerformanceMetrics.get_database_metrics(),
            'cache_metrics': PerformanceMetrics.get_cache_metrics(),
            'timestamp': time.time(),
        }


class LoadBalancer:
    """Simple load balancing for read replicas."""
    
    def __init__(self):
        self.replicas = []
        self.current_index = 0
    
    def add_replica(self, database_config):
        """Add a read replica."""
        self.replicas.append(database_config)
    
    def get_next_replica(self):
        """Get next replica using round-robin."""
        if not self.replicas:
            return None
        
        replica = self.replicas[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.replicas)
        return replica


class QueryOptimizer:
    """Query optimization utilities."""
    
    @staticmethod
    def optimize_student_queries():
        """Optimize student-related queries."""
        return {
            'select_related': ['user', 'school', 'class_name'],
            'prefetch_related': ['parents', 'medical_records'],
            'only': ['id', 'admission_number', 'status'],
        }
    
    @staticmethod
    def optimize_staff_queries():
        """Optimize staff-related queries."""
        return {
            'select_related': ['user', 'school', 'department'],
            'prefetch_related': ['leaves', 'performances'],
            'only': ['id', 'staff_id', 'employee_number', 'category'],
        }
    
    @staticmethod
    def optimize_file_queries():
        """Optimize file-related queries."""
        return {
            'select_related': ['created_by', 'current_holder', 'department'],
            'prefetch_related': ['movements', 'attachments'],
            'only': ['id', 'file_number', 'title', 'status'],
        }
    
    @staticmethod
    def optimize_attendance_queries():
        """Optimize attendance queries."""
        return {
            'select_related': ['student__user', 'recorded_by'],
            'only': ['id', 'student_id', 'date', 'status'],
        }
