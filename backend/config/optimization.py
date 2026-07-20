"""
Performance optimization utilities for Education District IV Portal.
Designed to handle 80,000+ students and 5,000+ staff efficiently.
"""

from django.db import models
from django.core.cache import cache
from functools import wraps
import hashlib
import json


def cache_result(timeout=300, key_prefix=''):
    """Cache function result for specified timeout."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(a) for a in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = f"ediv:{hashlib.md5(':'.join(key_parts).encode()).hexdigest()}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def clear_cache_pattern(pattern):
    """Clear all cache keys matching pattern."""
    from django.core.cache import cache
    from redis import Redis
    
    try:
        redis_client = Redis.from_url(cache._server)
        keys = redis_client.keys(f"ediv:{pattern}*")
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass


class OptimizedQuerySet:
    """Mixin for optimized querysets with select_related and prefetch_related."""
    
    @classmethod
    def get_optimized_queryset(cls):
        """Return queryset with optimized related object loading."""
        queryset = cls.objects.all()
        
        # Add select_related for ForeignKey fields
        select_related_fields = []
        prefetch_related_fields = []
        
        for field in cls._meta.fields:
            if isinstance(field, models.ForeignKey):
                select_related_fields.append(field.name)
        
        for field in cls._meta.many_to_many:
            prefetch_related_fields.append(field.name)
        
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)
        
        if prefetch_related_fields:
            queryset = queryset.prefetch_related(*prefetch_related_fields)
        
        return queryset


class BulkOperations:
    """Optimized bulk operations for large datasets."""
    
    @staticmethod
    def bulk_create_students(students_data, batch_size=1000):
        """Bulk create students efficiently."""
        from apps.students.models import Student
        
        students = []
        for data in students_data:
            students.append(Student(**data))
        
        return Student.objects.bulk_create(students, batch_size=batch_size)
    
    @staticmethod
    def bulk_update_students(students, fields, batch_size=1000):
        """Bulk update students efficiently."""
        from apps.students.models import Student
        
        return Student.objects.bulk_update(students, fields, batch_size=batch_size)
    
    @staticmethod
    def bulk_create_exam_results(results_data, batch_size=1000):
        """Bulk create exam results efficiently."""
        from apps.academics.models import ExamResult
        
        results = []
        for data in results_data:
            results.append(ExamResult(**data))
        
        return ExamResult.objects.bulk_create(results, batch_size=batch_size)
    
    @staticmethod
    def bulk_create_attendance(records_data, batch_size=1000):
        """Bulk create attendance records efficiently."""
        from apps.attendance.models import StudentAttendance
        
        records = []
        for data in records_data:
            records.append(StudentAttendance(**data))
        
        return StudentAttendance.objects.bulk_create(records, batch_size=batch_size)


class PaginationHelper:
    """Optimized pagination for large datasets."""
    
    @staticmethod
    def get_paginated_response(queryset, page, page_size=20):
        """Get paginated response with optimized queries."""
        from rest_framework.pagination import PageNumberPagination
        
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        
        page_obj = paginator.paginate_queryset(queryset, None)
        
        return {
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': page_obj
        }


class DatabaseOptimization:
    """Database optimization utilities."""
    
    @staticmethod
    def add_indexes():
        """Add performance indexes to frequently queried fields."""
        from django.db import connection
        
        indexes = [
            # Students table
            "CREATE INDEX IF NOT EXISTS idx_students_admission_number ON students_student(admission_number);",
            "CREATE INDEX IF NOT EXISTS idx_students_school ON students_student(school_id);",
            "CREATE INDEX IF NOT EXISTS idx_students_status ON students_student(status);",
            
            # Staff table
            "CREATE INDEX IF NOT EXISTS idx_staff_staff_id ON staff_staff(staff_id);",
            "CREATE INDEX IF NOT EXISTS idx_staff_school ON staff_staff(school_id);",
            "CREATE INDEX IF NOT EXISTS idx_staff_category ON staff_staff(category);",
            
            # Files table
            "CREATE INDEX IF NOT EXISTS idx_files_file_number ON files_file(file_number);",
            "CREATE INDEX IF NOT EXISTS idx_files_status ON files_file(status);",
            "CREATE INDEX IF NOT EXISTS idx_files_current_holder ON files_file(current_holder_id);",
            
            # Attendance table
            "CREATE INDEX IF NOT EXISTS idx_student_attendance_date ON attendance_studentattendance(date);",
            "CREATE INDEX IF NOT EXISTS idx_student_attendance_student ON attendance_studentattendance(student_id);",
            
            # Exam results
            "CREATE INDEX IF NOT EXISTS idx_exam_results_student ON academics_examresult(student_id);",
            "CREATE INDEX IF NOT EXISTS idx_exam_results_exam ON academics_examresult(exam_id);",
        ]
        
        with connection.cursor() as cursor:
            for index in indexes:
                try:
                    cursor.execute(index)
                except Exception:
                    pass
    
    @staticmethod
    def optimize_queries():
        """Common query optimizations."""
        return {
            'use_prefetch': True,
            'use_select_related': True,
            'use_only': True,
            'use_defer': True,
            'batch_size': 1000,
        }


class CacheWarming:
    """Cache warming utilities for frequently accessed data."""
    
    @staticmethod
    def warm_school_cache():
        """Warm cache with school data."""
        from apps.schools.models import School
        
        schools = School.objects.filter(is_active=True).values(
            'id', 'name', 'code', 'school_type', 'lga'
        )
        cache.set('ediv:schools:list', list(schools), timeout=3600)
    
    @staticmethod
    def warm_department_cache():
        """Warm cache with department data."""
        from apps.departments.models import Department
        
        departments = Department.objects.filter(is_active=True).values(
            'id', 'name', 'code', 'category'
        )
        cache.set('ediv:departments:list', list(departments), timeout=3600)
    
    @staticmethod
    def warm_subject_cache():
        """Warm cache with subject data."""
        from apps.academics.models import Subject
        
        subjects = Subject.objects.all().values('id', 'name', 'code', 'category')
        cache.set('ediv:subjects:list', list(subjects), timeout=3600)
    
    @staticmethod
    def warm_all_caches():
        """Warm all caches."""
        CacheWarming.warm_school_cache()
        CacheWarming.warm_department_cache()
        CacheWarming.warm_subject_cache()
