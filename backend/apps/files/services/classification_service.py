"""AI-Powered File Classification Service with expanded department routing."""
import re
from collections import Counter
from apps.files.models import File, FileClassification


class ClassificationService:
    """AI-powered file classification using keyword matching and rules."""

    # Expanded department keyword mappings matching enterprise routing
    DEPARTMENT_KEYWORDS = {
        'ADMIN_HR': [
            'staff', 'recruitment', 'leave', 'welfare', 'discipline',
            'transfer', 'promotion', 'appointment', 'salary', 'payroll',
            'human resource', 'hr', 'personnel', 'workforce', 'onboarding',
        ],
        'FINANCE': [
            'finance', 'budget', 'payment', 'revenue', 'account',
            'invoice', 'expenditure', 'procurement', 'financial',
            'audit', 'treasury', 'tax', 'funding', 'grant',
        ],
        'AUDIT': [
            'audit', 'inspection', 'compliance', 'fraud',
            'verification', 'investigation', 'review', 'internal control',
            'risk assessment', 'regulatory',
        ],
        'QA': [
            'inspection', 'report', 'evaluation', 'assessment',
            'performance', 'quality', 'standard', 'benchmark',
            'accreditation', 'monitoring',
        ],
        'CC': [
            'sports', 'french', 'culture', 'competition', 'club',
            'stem', 'co-curricular', 'extracurricular', 'debate',
            'quiz', 'athletics', 'music', 'drama',
        ],
        'EMIS': [
            'data', 'statistics', 'records', 'enrollment', 'reporting',
            'analysis', 'information', 'database', 'census',
            'demographic', 'metric', 'indicator',
        ],
        'PLANNING': [
            'strategic', 'policy', 'project', 'planning', 'development',
            'target', 'objective', 'initiative', 'roadmap', 'forecast',
            'budget planning', 'master plan',
        ],
        'PROCUREMENT': [
            'procurement', 'tender', 'bid', 'contract', 'supplier',
            'purchase', 'acquisition', 'vendor', 'quotation', 'rfq',
        ],
        'PUBLIC_AFFAIRS': [
            'media', 'communication', 'press', 'public', 'relations',
            'announcement', 'newsletter', 'website', 'social media',
            'branding', 'publicity', 'stakeholder',
        ],
        'SCHOOLS_ADMIN': [
            'school', 'principal', 'administration', 'supervision',
            'facility', 'infrastructure', 'maintenance', 'building',
            'classroom', 'laboratory', 'library',
        ],
    }

    # Urgency keywords
    URGENCY_KEYWORDS = {
        'URGENT': ['urgent', 'immediate', 'emergency', 'critical', 'asap', 'deadline'],
        'HIGH': ['important', 'priority', 'time-sensitive', 'expedite', 'essential'],
        'MEDIUM': ['review', 'follow-up', 'action required', 'standard', 'routine'],
        'LOW': ['information', 'for your information', 'fyi', 'update', 'minor'],
    }

    # Sensitivity keywords
    SENSITIVITY_KEYWORDS = {
        'RESTRICTED': ['confidential', 'restricted', 'sensitive', 'classified', 'internal use'],
        'PRIVATE': ['personal', 'staff only', 'private', 'individual'],
        'PUBLIC': ['public', 'announcement', 'general', 'circular', 'open'],
    }

    @staticmethod
    def _get_classification_scores(text):
        """Compute department, urgency, and sensitivity scores from text."""
        dept_scores = {}
        for dept, keywords in ClassificationService.DEPARTMENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                dept_scores[dept] = score / len(keywords)

        urgency_score = 'MEDIUM'
        for level, keywords in ClassificationService.URGENCY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                urgency_score = level
                break

        sensitivity_score = 'PUBLIC'
        for level, keywords in ClassificationService.SENSITIVITY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                sensitivity_score = level
                break

        all_keywords = []
        for keywords in ClassificationService.DEPARTMENT_KEYWORDS.values():
            all_keywords.extend([kw for kw in keywords if kw in text])

        return {
            'dept_scores': dept_scores,
            'urgency': urgency_score,
            'sensitivity': sensitivity_score,
            'keywords': list(set(all_keywords)),
        }

    @staticmethod
    def _compute_overall_confidence(dept_scores):
        """Compute overall confidence from department scores."""
        if dept_scores:
            best_score = max(dept_scores.values())
            return min(best_score * 2, 1.0)
        return 0.0

    @staticmethod
    def classify_file(file):
        """Classify a file based on its title, description, and tags."""
        text = f"{file.title} {file.description} {' '.join(file.tags if file.tags else [])}".lower()

        scores = ClassificationService._get_classification_scores(text)

        if scores['dept_scores']:
            best_dept = max(scores['dept_scores'], key=scores['dept_scores'].get)
            confidence = min(scores['dept_scores'][best_dept] * 2, 1.0)
        else:
            best_dept = ''
            confidence = 0.0

        overall_confidence = ClassificationService._compute_overall_confidence(scores['dept_scores'])

        classification, _ = FileClassification.objects.update_or_create(
            file=file,
            defaults={
                'suggested_department': best_dept,
                'department_confidence': confidence,
                'urgency': scores['urgency'],
                'sensitivity': scores['sensitivity'],
                'file_type_suggestion': file.file_type,
                'keywords': scores['keywords'][:10],
                'overall_confidence': overall_confidence,
            }
        )

        return classification

    @staticmethod
    def get_classification_suggestions(file):
        """Get classification suggestions without saving."""
        text = f"{file.title} {file.description} {' '.join(file.tags if file.tags else [])}".lower()

        scores = ClassificationService._get_classification_scores(text)

        if scores['dept_scores']:
            best_dept = max(scores['dept_scores'], key=scores['dept_scores'].get)
            confidence = min(scores['dept_scores'][best_dept] * 2, 1.0)
        else:
            best_dept = ''
            confidence = 0.0

        overall_confidence = ClassificationService._compute_overall_confidence(scores['dept_scores'])

        return {
            'suggested_department': best_dept,
            'department_confidence': confidence,
            'urgency': scores['urgency'],
            'sensitivity': scores['sensitivity'],
            'file_type_suggestion': file.file_type,
            'keywords': scores['keywords'][:10],
            'overall_confidence': overall_confidence,
            'all_dept_scores': scores['dept_scores'],
        }

    @staticmethod
    def bulk_classify(file_ids=None):
        """Classify multiple files at once."""
        qs = File.objects.all()
        if file_ids:
            qs = qs.filter(id__in=file_ids)
        results = []
        for file_obj in qs:
            results.append(ClassificationService.classify_file(file_obj))
        return results
