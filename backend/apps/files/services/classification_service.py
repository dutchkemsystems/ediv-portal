"""Classification service for AI-powered file categorization."""
from apps.files.models import File, FileClassification


class ClassificationService:
    """AI-powered file classification using keyword matching and rules."""

    # Department keyword mappings
    DEPARTMENT_KEYWORDS = {
        'Finance': [
            'budget', 'expenditure', 'revenue', 'financial', 'invoice',
            'payment', 'account', 'audit', 'procurement',
        ],
        'Academic': [
            'curriculum', 'exam', 'result', 'student', 'teacher',
            'academic', 'syllabus', 'grading', 'promotion',
        ],
        'HR': [
            'staff', 'appointment', 'transfer', 'promotion', 'discipline',
            'leave', 'salary', 'recruitment',
        ],
        'Administration': [
            'meeting', 'minutes', 'memo', 'circular', 'office',
            'admin', 'general',
        ],
        'Inspection': [
            'inspection', 'monitoring', 'compliance', 'verification',
            'assessment',
        ],
        'Discipline': [
            'complaint', 'misconduct', 'disciplinary', 'investigation',
            'suspension',
        ],
        'Transport': [
            'bus', 'vehicle', 'transport', 'route', 'driver',
            'maintenance',
        ],
    }

    # Urgency keywords
    URGENCY_KEYWORDS = {
        'URGENT': ['urgent', 'immediate', 'emergency', 'critical', 'asap', 'deadline'],
        'HIGH': ['important', 'priority', 'time-sensitive', 'expedite'],
        'MEDIUM': ['review', 'follow-up', 'action required'],
        'LOW': ['information', 'for your information', 'fyi', 'update'],
    }

    # Sensitivity keywords
    SENSITIVITY_KEYWORDS = {
        'RESTRICTED': ['confidential', 'restricted', 'sensitive', 'private', 'classified'],
        'PRIVATE': ['personal', 'staff only', 'internal use'],
        'PUBLIC': ['public', 'announcement', 'general', 'circular'],
    }

    @staticmethod
    def _get_classification_scores(text):
        """
        Compute department, urgency, and sensitivity scores from text.

        Returns a dict with keys: dept_scores, urgency, sensitivity, keywords
        """
        # Score departments
        dept_scores = {}
        for dept, keywords in ClassificationService.DEPARTMENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                dept_scores[dept] = score / len(keywords)

        # Score urgency - first match wins (ordered by priority)
        urgency_score = 'MEDIUM'
        for level, keywords in ClassificationService.URGENCY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                urgency_score = level
                break

        # Score sensitivity - first match wins (ordered by specificity)
        sensitivity_score = 'PUBLIC'
        for level, keywords in ClassificationService.SENSITIVITY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                sensitivity_score = level
                break

        # Extract matched keywords
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
            return min(best_score * 2, 1.0)  # Normalize to 0-1
        return 0.0

    @staticmethod
    def classify_file(file):
        """
        Classify a file based on its title, description, and tags.
        Returns FileClassification with confidence scores.
        """
        text = f"{file.title} {file.description} {' '.join(file.tags if file.tags else [])}".lower()

        scores = ClassificationService._get_classification_scores(text)

        # Determine best department
        if scores['dept_scores']:
            best_dept = max(scores['dept_scores'], key=scores['dept_scores'].get)
            confidence = min(scores['dept_scores'][best_dept] * 2, 1.0)
        else:
            best_dept = ''
            confidence = 0.0

        overall_confidence = ClassificationService._compute_overall_confidence(
            scores['dept_scores']
        )

        # Create or update classification
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
        """
        Get classification suggestions without saving.
        Returns a dict instead of a FileClassification instance.
        """
        text = f"{file.title} {file.description} {' '.join(file.tags if file.tags else [])}".lower()

        scores = ClassificationService._get_classification_scores(text)

        if scores['dept_scores']:
            best_dept = max(scores['dept_scores'], key=scores['dept_scores'].get)
            confidence = min(scores['dept_scores'][best_dept] * 2, 1.0)
        else:
            best_dept = ''
            confidence = 0.0

        overall_confidence = ClassificationService._compute_overall_confidence(
            scores['dept_scores']
        )

        return {
            'suggested_department': best_dept,
            'department_confidence': confidence,
            'urgency': scores['urgency'],
            'sensitivity': scores['sensitivity'],
            'file_type_suggestion': file.file_type,
            'keywords': scores['keywords'][:10],
            'overall_confidence': overall_confidence,
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
