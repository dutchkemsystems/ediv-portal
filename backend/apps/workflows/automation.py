"""Agentic Automation System for Education District IV Portal.

Automatically distributes files and mails to correct departments and units
based on existing workflow definitions and content analysis.
"""

import datetime
import logging
import re

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from apps.departments.models import Department, Unit
from apps.files.models import File, FileCategory, FileMovement, FileType
from apps.files.services.file_movement_service import FileMovementService
from apps.files.services.notification_service import NotificationService
from apps.registry.models import (
    Correspondence,
    Document,
    DocumentType,
    MemoApproval,
    MemoCirculation,
    MemoWorkflow,
)
from apps.workflows.models import Task, WorkflowInstance
from apps.workflows.services.workflow_service import WorkflowService
from apps.workflows.workflow_definitions import (
    ALL_WORKFLOWS,
    DEPARTMENT_CODES,
    FILE_CATEGORIES,
    SECURITY_CLASSIFICATIONS,
)

User = get_user_model()
logger = logging.getLogger(__name__)

DEPARTMENT_KEYWORDS = {
    "HR": [
        "human resource",
        "staff",
        "employee",
        "recruitment",
        "appointment",
        "promotion",
        "discipline",
        "leave",
        "training",
        "capacity building",
        "staff welfare",
        "human resource management",
        "personnel",
        "staffing",
        "orientation",
        "induction",
        "performance appraisal",
        "staff record",
        "human capital",
        "labour",
        "workforce",
        "deployment",
        "transfer",
    ],
    "FIN": [
        "finance",
        "budget",
        "expenditure",
        "revenue",
        "accounting",
        "financial",
        "payment",
        "invoice",
        "procurement fund",
        "audit query",
        "financial report",
        "treasury",
        "cash flow",
        "appropriation",
        "fiscal",
        "grant disbursement",
        "fund allocation",
        "disbursement",
        "reimbursement",
        "virement",
        "financial statement",
    ],
    "AUD": [
        "audit",
        "internal control",
        "compliance",
        "fraud",
        "forensic",
        "risk assessment",
        "audit report",
        "audit finding",
        "audit recommendation",
        "financial audit",
        "operational audit",
        "management audit",
        "audit trail",
        "reconciliation",
        "verification",
    ],
    "QA": [
        "quality assurance",
        "inspection",
        "standard",
        "accreditation",
        "quality control",
        "assessment",
        "evaluation",
        "examination",
        "quality standard",
        "benchmark",
        "performance indicator",
        "school inspection",
        "inspection report",
        "quality improvement",
        "monitoring and evaluation",
        "compliance check",
    ],
    "CC": [
        "co-curricular",
        "sports",
        "cultural",
        "club",
        "society",
        "extracurricular",
        "inter-school",
        "competition",
        "tournament",
        "activities",
        "games",
        "athletics",
        "debate",
        "science fair",
        "cultural festival",
        "sports day",
        "co-curricular activity",
    ],
    "FRENCH": [
        "french",
        "francophone",
        "french language",
        "french unit",
        "bilingual",
        "langue francaise",
        "french immersion",
        "french programme",
        "french teacher",
        "french curriculum",
        "french examination",
    ],
    "EMIS": [
        "emis",
        "education management information",
        "data",
        "statistics",
        "information system",
        "database",
        "reporting",
        "data collection",
        "school data",
        "student data",
        "enrollment data",
        "census",
        "data analysis",
        "information management",
        "school mapping",
    ],
    "PLAN": [
        "planning",
        "strategic plan",
        "development plan",
        "project",
        "programme",
        "annual plan",
        "budget planning",
        "needs assessment",
        "development",
        "implementation plan",
        "action plan",
        "master plan",
        "sector plan",
        "education planning",
        "policy planning",
    ],
    "PROC": [
        "procurement",
        "tender",
        "bid",
        "supply",
        "purchase",
        "requisition",
        "quotation",
        "contract award",
        "vendor",
        "supplier",
        "procurement process",
        "bidding",
        "evaluation committee",
        "procurement plan",
        "public procurement",
    ],
    "PA": [
        "public affairs",
        "public relation",
        "communication",
        "media",
        "press",
        "publicity",
        "spokesperson",
        "public information",
        "community relation",
        "stakeholder engagement",
        "public engagement",
        "media relation",
        "news",
        "press release",
    ],
    "SA": [
        "student affair",
        "school admin",
        "school management",
        "student welfare",
        "admission",
        "enrollment",
        "registration",
        "student record",
        "school head",
        "principal",
        "vice principal",
        "school administration",
        "student discipline",
        "student support",
        "guidance and counselling",
    ],
    "REG": [
        "registry",
        "correspondence",
        "mail",
        "dispatch",
        "filing",
        "document management",
        "record keeping",
        "archival",
        "reference number",
        "incoming mail",
        "outgoing mail",
        "letter",
        "memo",
        "circular",
        "internal memo",
        "official correspondence",
    ],
    "TG": [
        "tutor general",
        "permanent secretary",
        "management",
        "policy",
        "governance",
        "strategic direction",
        "office of the tg",
        "tg office",
        "executive decision",
        "board",
        "ministry directive",
    ],
}

FILE_CATEGORY_KEYWORDS = {
    "FIN": [
        "budget",
        "financial",
        "invoice",
        "payment",
        "expenditure",
        "revenue",
        "fund",
        "appropriation",
    ],
    "PROC": [
        "procurement",
        "tender",
        "bid",
        "supply",
        "contract",
        "purchase",
        "quotation",
    ],
    "ACAD": [
        "academic",
        "curriculum",
        "examination",
        "result",
        "grading",
        "syllabus",
        "teaching",
    ],
    "ADMIN": ["administrative", "general", "staff", "office", "management"],
    "INSP": ["inspection", "monitoring", "evaluation", "compliance", "quality"],
    "DISC": ["disciplinary", "misconduct", "complaint", "grievance", "sanction"],
    "COCC": ["co-curricular", "sports", "cultural", "club", "activities"],
    "POL": ["policy", "guideline", "regulation", "directive", "procedure"],
    "CORR": ["correspondence", "letter", "memorandum", "circular", "communication"],
}

URGENCY_KEYWORDS = {
    "URGENT": [
        "urgent",
        "emergency",
        "immediate",
        "critical",
        "asap",
        "time-sensitive",
        "deadline today",
    ],
    "HIGH": [
        "important",
        "priority",
        "expedite",
        "fast track",
        "deadline approaching",
        "overdue",
    ],
    "NORMAL": ["routine", "standard", "regular", "normal"],
    "LOW": ["information", "fyi", "note", "for record", "low priority"],
}


class AgenticRouter:
    """Intelligent file/mail router that analyzes documents and routes to correct departments."""

    def __init__(self):
        self._department_cache = None
        self._user_cache = {}

    def _get_departments(self):
        if self._department_cache is None:
            self._department_cache = {
                dept.code: dept for dept in Department.objects.filter(is_active=True)
            }
        return self._department_cache

    def _get_department_users(self, role):
        cache_key = f"role_{role}"
        if cache_key not in self._user_cache:
            self._user_cache[cache_key] = list(
                User.objects.filter(role=role, is_active=True).order_by("id")
            )
        return self._user_cache[cache_key]

    def determine_department(self, text):
        if not text:
            return None
        text_lower = text.lower()
        scores = {}
        for dept_code, keywords in DEPARTMENT_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += len(keyword.split())
            if score > 0:
                scores[dept_code] = score
        if not scores:
            return "REG"
        return max(scores, key=scores.get)

    def determine_file_category(self, text):
        if not text:
            return "ADMIN"
        text_lower = text.lower()
        scores = {}
        for category, keywords in FILE_CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        if not scores:
            return "ADMIN"
        return max(scores, key=scores.get)

    def determine_urgency(self, text):
        if not text:
            return "NORMAL"
        text_lower = text.lower()
        for urgency, keywords in URGENCY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    return urgency
        return "NORMAL"

    def determine_security_classification(self, text):
        if not text:
            return "CONFIDENTIAL"
        text_lower = text.lower()
        top_secret_indicators = ["top secret", "eyes only", "highest classification"]
        restricted_indicators = ["restricted", "limited distribution", "need to know"]
        confidential_indicators = ["confidential", "sensitive", "internal use"]
        for indicator in top_secret_indicators:
            if indicator in text_lower:
                return "TOP_SECRET"
        for indicator in restricted_indicators:
            if indicator in text_lower:
                return "RESTRICTED"
        for indicator in confidential_indicators:
            if indicator in text_lower:
                return "CONFIDENTIAL"
        return "PUBLIC"

    def get_department_head(self, department_code):
        departments = self._get_departments()
        dept = departments.get(department_code)
        if dept and dept.head:
            return dept.head
        role_map = {
            "TG": "TG_PS",
            "HR": "HR",
            "FIN": "FIN",
            "AUD": "AUDIT",
            "QA": "QA",
            "CC": "CC",
            "FRENCH": "FRENCH",
            "EMIS": "EMIS",
            "PLAN": "PLAN",
            "PROC": "PROC",
            "PA": "PA",
            "SA": "SA",
            "REG": "REG",
        }
        role = role_map.get(department_code)
        if role:
            users = self._get_department_users(role)
            if users:
                return users[0]
        return User.objects.filter(role="SYSADMIN", is_active=True).first()

    def get_department_staff(self, department_code, exclude_head=True):
        head = self.get_department_head(department_code)
        departments = self._get_departments()
        dept = departments.get(department_code)
        if not dept:
            return []
        staff = list(
            User.objects.filter(
                Q(departments__head=dept) | Q(units__department=dept),
                is_active=True,
            ).distinct()
        )
        if exclude_head and head:
            staff = [u for u in staff if u.id != head.id]
        return staff

    def auto_assign_task(self, task, workflow_step):
        try:
            assigned_role = (
                workflow_step.assigned_role
                if hasattr(workflow_step, "assigned_role")
                else None
            )
            if assigned_role:
                candidate = User.objects.filter(
                    role=assigned_role, is_active=True
                ).first()
                if candidate:
                    task.assigned_to = candidate
                    task.save(update_fields=["assigned_to", "updated_at"])
                    return candidate
        except Exception as e:
            logger.error(f"Auto-assign failed for task {task.id}: {e}")
        return None

    def route_incoming_mail(self, mail):
        try:
            analysis_text = " ".join(
                filter(
                    None,
                    [
                        getattr(mail, "subject", "") or "",
                        getattr(mail, "content", "") or getattr(mail, "body", "") or "",
                        getattr(mail, "sender", "") or "",
                    ],
                )
            )
            dept_code = self.determine_department(analysis_text)
            dept_head = self.get_department_head(dept_code)
            urgency = self.determine_urgency(analysis_text)
            classification = self.determine_security_classification(analysis_text)
            result = {
                "department_code": dept_code,
                "department_head": dept_head,
                "urgency": urgency,
                "classification": classification,
                "department_name": DEPARTMENT_CODES.get(dept_code, "Registry"),
            }
            if hasattr(mail, "assigned_department_id"):
                departments = self._get_departments()
                dept = departments.get(dept_code)
                if dept:
                    mail.assigned_department = dept
                    mail.save(update_fields=["assigned_department", "updated_at"])
            logger.info(
                f"Mail routed: dept={dept_code}, head={dept_head}, urgency={urgency}"
            )
            return result
        except Exception as e:
            logger.error(f"Failed to route incoming mail: {e}")
            return {
                "department_code": "REG",
                "department_head": self.get_department_head("REG"),
                "urgency": "NORMAL",
                "classification": "CONFIDENTIAL",
                "department_name": "Registry",
            }

    def route_file(self, file):
        try:
            analysis_text = " ".join(
                filter(
                    None,
                    [
                        file.title or "",
                        file.description or "",
                        " ".join(file.tags or []),
                    ],
                )
            )
            dept_code = self.determine_department(analysis_text)
            dept_head = self.get_department_head(dept_code)
            category = self.determine_file_category(analysis_text)
            urgency = self.determine_urgency(analysis_text)
            classification = self.determine_security_classification(analysis_text)
            departments = self._get_departments()
            dept = departments.get(dept_code)
            if dept:
                file.assigned_department = dept
            if not file.department and dept:
                file.department = dept
            file.file_category = category
            file.priority = urgency
            file.classification = classification
            file.save(
                update_fields=[
                    "assigned_department",
                    "department",
                    "file_category",
                    "priority",
                    "classification",
                    "updated_at",
                ]
            )
            result = {
                "department_code": dept_code,
                "department_head": dept_head,
                "category": category,
                "urgency": urgency,
                "classification": classification,
                "department_name": DEPARTMENT_CODES.get(dept_code, "Registry"),
            }
            logger.info(
                f"File {file.file_number} routed: dept={dept_code}, "
                f"cat={category}, urgency={urgency}"
            )
            return result
        except Exception as e:
            logger.error(f"Failed to route file {file.file_number}: {e}")
            return {
                "department_code": "REG",
                "department_head": self.get_department_head("REG"),
                "category": file.file_category or "ADMIN",
                "urgency": file.priority or "NORMAL",
                "classification": file.classification or "CONFIDENTIAL",
                "department_name": "Registry",
            }

    def route_memo(self, memo):
        try:
            document = memo.document if hasattr(memo, "document") else memo
            analysis_text = " ".join(
                filter(
                    None,
                    [
                        getattr(document, "title", "") or "",
                        getattr(document, "content", "") or "",
                    ],
                )
            )
            dept_code = self.determine_department(analysis_text)
            urgency = self.determine_urgency(analysis_text)
            classification = self.determine_security_classification(analysis_text)
            recipients = []
            dept_head = self.get_department_head(dept_code)
            if dept_head:
                recipients.append(dept_head)
            staff = self.get_department_staff(dept_code)
            recipients.extend(staff)
            tg_users = self._get_department_users("TG_PS")
            for u in tg_users:
                if u.id not in [r.id for r in recipients]:
                    recipients.append(u)
            result = {
                "department_code": dept_code,
                "recipients": recipients,
                "urgency": urgency,
                "classification": classification,
                "department_name": DEPARTMENT_CODES.get(dept_code, "Registry"),
            }
            logger.info(
                f"Memo routed: dept={dept_code}, recipients={len(recipients)}, "
                f"urgency={urgency}"
            )
            return result
        except Exception as e:
            logger.error(f"Failed to route memo: {e}")
            return {
                "department_code": "REG",
                "recipients": [],
                "urgency": "NORMAL",
                "classification": "CONFIDENTIAL",
                "department_name": "Registry",
            }


class MailDistributor:
    """Automatic mail distribution system for incoming and outgoing mail."""

    def __init__(self):
        self.router = AgenticRouter()

    def classify_mail(self, mail):
        text = " ".join(
            filter(
                None,
                [
                    getattr(mail, "subject", "") or "",
                    getattr(mail, "content", "") or getattr(mail, "body", "") or "",
                    getattr(mail, "sender", "") or "",
                ],
            )
        )
        doc_type = "CORRESPONDENCE"
        text_lower = text.lower()
        type_keywords = {
            "MEMO": ["memo", "memorandum", "internal memo"],
            "CIRCULAR": ["circular", "circular letter", "directive"],
            "REPORT": ["report", "annual report", "status report"],
            "CONTRACT": ["contract", "agreement", "memorandum of understanding"],
            "INVOICE": ["invoice", "bill", "statement"],
            "LETTER": ["letter", "dear sir", "dear madam", "yours faithfully"],
        }
        for dtype, keywords in type_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    doc_type = dtype
                    break
            if doc_type != "CORRESPONDENCE":
                break
        urgency = self.router.determine_urgency(text)
        classification = self.router.determine_security_classification(text)
        dept_code = self.router.determine_department(text)
        return {
            "document_type": doc_type,
            "urgency": urgency,
            "classification": classification,
            "department_code": dept_code,
            "requires_response": urgency in ("URGENT", "HIGH"),
        }

    def assign_action(self, mail, action_required, deadline=None, assigned_to=None):
        try:
            classification = self.classify_mail(mail)
            if assigned_to is None:
                dept_code = classification["department_code"]
                assigned_to = self.router.get_department_head(dept_code)
            if assigned_to is None:
                assigned_to = User.objects.filter(
                    role="SYSADMIN", is_active=True
                ).first()
            if assigned_to is None:
                logger.warning("No assignee found for mail action")
                return None
            document = None
            if hasattr(mail, "document"):
                document = mail.document
            elif isinstance(mail, Document):
                document = mail
            elif isinstance(mail, dict):
                title = mail.get("title", "Untitled Mail")
                ref_number = mail.get(
                    "reference_number", f"EDIV/MAIL/{timezone.now().year}/AUTO"
                )
                sender_name = mail.get("sender", "Unknown")
                document = Document.objects.create(
                    reference_number=ref_number,
                    title=title,
                    document_type=classification.get("document_type", "CORRESPONDENCE"),
                    content=mail.get("content", ""),
                    created_by=assigned_to,
                    status="PENDING",
                    classification=classification.get("classification", "CONFIDENTIAL"),
                )
                Correspondence.objects.create(
                    document=document,
                    direction="INCOMING",
                    sender=sender_name,
                    recipient=assigned_to.get_full_name() or assigned_to.username,
                    date_received=timezone.now().date(),
                    subject=title,
                    is_urgent=classification.get("urgency") in ("URGENT", "HIGH"),
                    requires_response=classification.get("requires_response", False),
                    response_deadline=deadline,
                )
            workflow_type = None
            doc_type = classification.get("document_type", "CORRESPONDENCE")
            if doc_type == "MEMO":
                workflow_type = "INTERNAL_MEMO"
            elif doc_type in ("CORRESPONDENCE", "LETTER"):
                workflow_type = "INCOMING_MAIL"
            elif doc_type == "CIRCULAR":
                workflow_type = "INTERNAL_MEMO"
            elif doc_type == "CONTRACT":
                workflow_type = "DEPARTMENT_TO_DEPARTMENT"
            else:
                workflow_type = "INCOMING_MAIL"
            ref_number = getattr(document, "reference_number", None)
            if ref_number is None:
                ref_number = (
                    f"EDIV/MAIL/{timezone.now().year}/{timezone.now().timestamp():.0f}"
                )
            try:
                instance = WorkflowService.start_instance(
                    workflow_type=workflow_type,
                    initiated_by=assigned_to,
                    reference_number=ref_number,
                    data={
                        "document_id": document.id if document else None,
                        "action_required": action_required,
                        "classification": classification,
                        "deadline": (
                            deadline.isoformat()
                            if hasattr(deadline, "isoformat")
                            else str(deadline)
                            if deadline
                            else None
                        ),
                    },
                )
                logger.info(
                    f"Workflow instance {instance.reference_number} created for mail"
                )
            except Exception as e:
                logger.warning(f"Could not start workflow instance: {e}")
            result = {
                "assignee": assigned_to,
                "document": document,
                "classification": classification,
                "action_required": action_required,
                "deadline": deadline,
            }
            logger.info(
                f"Mail action assigned: {assigned_to.get_full_name()}, "
                f"action={action_required}, deadline={deadline}"
            )
            return result
        except Exception as e:
            logger.error(f"Failed to assign mail action: {e}")
            return None

    def notify_recipients(self, mail, recipients):
        results = []
        subject = getattr(mail, "subject", None) or getattr(
            mail, "title", "Mail Notification"
        )
        if isinstance(mail, Document):
            subject = f"New Mail: {mail.title}"
            body = f"You have been assigned a new mail item.\n\nReference: {mail.reference_number}\nSubject: {mail.title}"
        elif isinstance(mail, dict):
            subject = mail.get("subject", "Mail Notification")
            body = mail.get("body", "You have been assigned a new mail item.")
        else:
            body = f"You have been assigned a new mail item: {subject}"
        for recipient in recipients:
            try:
                result = NotificationService.send_notification(
                    recipient=recipient,
                    subject=f"[Mail Distribution] {subject}",
                    message=body,
                    notification_type="MAIL_ASSIGNMENT",
                    priority="HIGH",
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Notification failed for {recipient}: {e}")
                results.append({"success": False, "error": str(e)})
        return results

    @transaction.atomic
    def distribute(self, mail):
        try:
            if isinstance(mail, dict):
                classification = self.classify_mail(mail)
                dept_code = classification["department_code"]
                dept_head = self.router.get_department_head(dept_code)
                if dept_head is None:
                    dept_head = User.objects.filter(
                        role="SYSADMIN", is_active=True
                    ).first()
                result = self.assign_action(
                    mail=mail,
                    action_required="Process incoming mail",
                    deadline=None,
                    assigned_to=dept_head,
                )
                if result and result.get("assignee"):
                    self.notify_recipients(mail, [result["assignee"]])
                return {
                    "success": True,
                    "distribution": result,
                    "classification": classification,
                }
            classification = self.classify_mail(mail)
            dept_code = classification["department_code"]
            dept_head = self.router.get_department_head(dept_code)
            if dept_head is None:
                dept_head = User.objects.filter(role="SYSADMIN", is_active=True).first()
            result = self.assign_action(
                mail=mail,
                action_required="Process incoming mail",
                deadline=None,
                assigned_to=dept_head,
            )
            if result and result.get("assignee"):
                self.notify_recipients(mail, [result["assignee"]])
            return {
                "success": True,
                "distribution": result,
                "classification": classification,
            }
        except Exception as e:
            logger.error(f"Mail distribution failed: {e}")
            return {"success": False, "error": str(e)}

    @transaction.atomic
    def escalate(self, mail, reason="Auto-escalated"):
        try:
            classification = self.classify_mail(mail)
            escalation_chain = [
                User.objects.filter(role="SYSADMIN", is_active=True).first(),
                User.objects.filter(role="TG_PS", is_active=True).first(),
            ]
            escalation_chain = [u for u in escalation_chain if u is not None]
            if not escalation_chain:
                return {"success": False, "error": "No escalation targets available"}
            target = escalation_chain[0]
            document = mail if isinstance(mail, Document) else None
            if document and hasattr(document, "status"):
                document.status = "APPROVED"
                document.save(update_fields=["status", "updated_at"])
            subject = f"ESCALATION: {getattr(mail, 'subject', None) or getattr(mail, 'title', 'Mail Item')}"
            message = (
                f"This mail item has been escalated.\n\n"
                f"Reason: {reason}\n"
                f"Classification: {classification.get('classification', 'CONFIDENTIAL')}\n"
                f"Department: {DEPARTMENT_CODES.get(classification.get('department_code', 'REG'), 'Registry')}"
            )
            NotificationService.send_notification(
                recipient=target,
                subject=subject,
                message=message,
                notification_type="MAIL_ESCALATION",
                priority="URGENT",
            )
            logger.info(f"Mail escalated to {target.get_full_name()}: {reason}")
            return {"success": True, "escalated_to": target, "reason": reason}
        except Exception as e:
            logger.error(f"Mail escalation failed: {e}")
            return {"success": False, "error": str(e)}

    def bulk_distribute(self, mails):
        results = []
        for mail in mails:
            result = self.distribute(mail)
            results.append(result)
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        logger.info(f"Bulk mail distribution: {successful} successful, {failed} failed")
        return {
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "details": results,
        }


class FileDistributor:
    """Automatic file distribution system based on workflow and content analysis."""

    def __init__(self):
        self.router = AgenticRouter()

    @transaction.atomic
    def distribute(self, file):
        try:
            route_result = self.router.route_file(file)
            dept_code = route_result["department_code"]
            dept_head = route_result.get("department_head")
            if dept_head is None:
                dept_head = self.router.get_department_head(dept_code)
            if dept_head is None:
                dept_head = User.objects.filter(role="SYSADMIN", is_active=True).first()
            if dept_head is None:
                return {"success": False, "error": "No department head found"}
            movement = FileMovementService.move_file(
                file=file,
                from_holder=file.created_by,
                to_holder=dept_head,
                action="FORWARDED",
                remarks=f"Auto-routed to {DEPARTMENT_CODES.get(dept_code, 'Registry')} department",
            )
            NotificationService.send_notification(
                recipient=dept_head,
                subject=f"File {file.file_number} assigned to you",
                message=(
                    f"File '{file.title}' ({file.file_number}) has been "
                    f"automatically routed to your department.\n"
                    f"Priority: {file.get_priority_display()}\n"
                    f"Category: {file.get_file_category_display()}"
                ),
                file=file,
                notification_type="FILE_ASSIGNMENT",
                priority=file.priority,
            )
            logger.info(
                f"File {file.file_number} distributed to {dept_head.get_full_name()} "
                f"in {DEPARTMENT_CODES.get(dept_code)}"
            )
            return {
                "success": True,
                "movement": movement,
                "route": route_result,
                "assignee": dept_head,
            }
        except Exception as e:
            logger.error(f"File distribution failed for {file.file_number}: {e}")
            return {"success": False, "error": str(e)}

    def determine_next_holder(self, file):
        try:
            current_step = file.current_workflow_step or 0
            direction = file.direction or "INCOMING"
            next_step_info = FileMovementService._get_next_step(current_step, direction)
            if not next_step_info:
                return None
            role = next_step_info.get("role", "")
            role_user_map = {
                "TG_PS": "TG_PS",
                "REG_OFF": "REG_OFF",
                "SA_OFF": "SA_OFF",
                "TCH": "TCH",
                "REG": "REG",
            }
            django_role = role_user_map.get(role, "SYSADMIN")
            candidate = User.objects.filter(role=django_role, is_active=True).first()
            if candidate:
                return candidate
            dept_code = (
                file.assigned_department.code if file.assigned_department else "REG"
            )
            return self.router.get_department_head(dept_code)
        except Exception as e:
            logger.error(f"Failed to determine next holder: {e}")
            return None

    @transaction.atomic
    def bulk_distribute(self, files):
        results = []
        for file_obj in files:
            result = self.distribute(file_obj)
            results.append(result)
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        logger.info(f"Bulk file distribution: {successful} successful, {failed} failed")
        return {
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "details": results,
        }

    def rebalance_workload(self, department):
        try:
            if isinstance(department, str):
                department = Department.objects.filter(
                    code=department, is_active=True
                ).first()
            if department is None:
                return {"success": False, "error": "Department not found"}
            active_files = File.objects.filter(
                assigned_department=department,
                status__in=["ACTIVE", "PENDING", "IN_TRANSIT", "UNDER_REVIEW"],
            ).select_related("current_holder")
            holder_counts = {}
            for f in active_files:
                if f.current_holder:
                    holder_id = f.current_holder_id
                    holder_counts[holder_id] = holder_counts.get(holder_id, 0) + 1
            if not holder_counts:
                return {"success": True, "rebalanced": 0}
            max_holder_id = max(holder_counts, key=holder_counts.get)
            min_holder_id = min(holder_counts, key=holder_counts.get)
            max_count = holder_counts[max_holder_id]
            min_count = holder_counts[min_holder_id]
            rebalanced = 0
            if max_count - min_count > 2:
                excess_files = File.objects.filter(
                    assigned_department=department,
                    current_holder_id=max_holder_id,
                    status__in=["ACTIVE", "PENDING"],
                ).select_related("current_holder")[:2]
                target_user = User.objects.filter(
                    id=min_holder_id, is_active=True
                ).first()
                if target_user:
                    for f in excess_files:
                        try:
                            FileMovementService.move_file(
                                file=f,
                                from_holder=f.current_holder,
                                to_holder=target_user,
                                action="FORWARDED",
                                remarks="Workload rebalancing",
                            )
                            rebalanced += 1
                        except Exception as e:
                            logger.error(
                                f"Rebalance failed for file {f.file_number}: {e}"
                            )
            logger.info(
                f"Workload rebalance for {department.code}: {rebalanced} files moved"
            )
            return {"success": True, "rebalanced": rebalanced}
        except Exception as e:
            logger.error(f"Workload rebalance failed: {e}")
            return {"success": False, "error": str(e)}


class DepartmentAgent:
    """Per-department automation agent that monitors and processes department items."""

    def __init__(self, department_code=None):
        self.department_code = department_code
        self.router = AgenticRouter()
        self.mail_distributor = MailDistributor()
        self.file_distributor = FileDistributor()

    def _get_department(self, department_code=None):
        code = department_code or self.department_code
        if code is None:
            return None
        return Department.objects.filter(code=code, is_active=True).first()

    def _get_department_items(self, department, item_type="all"):
        items = {"pending_mails": [], "pending_files": [], "overdue_items": []}
        if item_type in ("all", "mail"):
            items["pending_mails"] = (
                Document.objects.filter(
                    Q(assigned_department=department) | Q(department=department),
                    status__in=["DRAFT", "PENDING"],
                )
                .select_related("created_by")
                .order_by("-created_at")[:50]
            )
        if item_type in ("all", "file"):
            items["pending_files"] = (
                File.objects.filter(
                    Q(assigned_department=department) | Q(department=department),
                    status__in=["ACTIVE", "PENDING", "IN_TRANSIT", "UNDER_REVIEW"],
                )
                .select_related("current_holder", "created_by")
                .order_by("-created_at")[:50]
            )
        if item_type in ("all", "overdue"):
            items["overdue_items"] = File.objects.filter(
                Q(assigned_department=department) | Q(department=department),
                expected_completion_date__lt=timezone.now().date(),
                status__in=["ACTIVE", "PENDING", "IN_TRANSIT", "UNDER_REVIEW"],
                escalation_status="NORMAL",
            ).select_related("current_holder", "created_by")
        return items

    @transaction.atomic
    def process_department_mail(self, department_code=None):
        department = self._get_department(department_code)
        if department is None:
            return {"success": False, "error": "Department not found"}
        items = self._get_department_items(department, "mail")
        pending_mails = items["pending_mails"]
        processed = 0
        errors = 0
        for mail in pending_mails:
            try:
                correspondence = (
                    mail.correspondence if hasattr(mail, "correspondence") else None
                )
                text = " ".join(
                    filter(
                        None,
                        [
                            mail.title or "",
                            mail.content or "",
                            correspondence.subject if correspondence else "",
                            correspondence.sender if correspondence else "",
                        ],
                    )
                )
                urgency = self.router.determine_urgency(text)
                classification = self.router.determine_security_classification(text)
                mail.status = "PENDING"
                mail.classification = classification
                mail.save(update_fields=["status", "classification", "updated_at"])
                department_head = department.head
                if department_head and mail.created_by != department_head:
                    staff = (
                        User.objects.filter(
                            is_active=True,
                        )
                        .filter(
                            Q(departments__head=department)
                            | Q(units__department=department),
                        )
                        .exclude(id=department_head.id)
                        .first()
                    )
                    assignee = staff or department_head
                else:
                    assignee = (
                        department_head
                        or User.objects.filter(role="SYSADMIN", is_active=True).first()
                    )
                if assignee:
                    NotificationService.send_notification(
                        recipient=assignee,
                        subject=f"[{department.name}] Mail requires attention: {mail.title}",
                        message=(
                            f"A new mail item requires your attention.\n\n"
                            f"Reference: {mail.reference_number}\n"
                            f"Subject: {mail.title}\n"
                            f"Priority: {urgency}"
                        ),
                        notification_type="MAIL_ASSIGNMENT",
                        priority=urgency,
                    )
                processed += 1
            except Exception as e:
                logger.error(f"Failed to process mail {mail.id}: {e}")
                errors += 1
        logger.info(
            f"Department {department.code} mail processing: "
            f"{processed} processed, {errors} errors"
        )
        return {
            "success": True,
            "department": department.code,
            "processed": processed,
            "errors": errors,
            "total": len(pending_mails),
        }

    def generate_daily_summary(self, department_code=None):
        department = self._get_department(department_code)
        if department is None:
            return {"success": False, "error": "Department not found"}
        today = timezone.now().date()
        items = self._get_department_items(department, "all")
        total_mails = Document.objects.filter(
            Q(assigned_department=department) | Q(department=department),
            created_at__date=today,
        ).count()
        total_files = File.objects.filter(
            Q(assigned_department=department) | Q(department=department),
            created_at__date=today,
        ).count()
        completed_files = FileMovement.objects.filter(
            file__assigned_department=department,
            action="ARCHIVED",
            movement_date__date=today,
        ).count()
        overdue_count = (
            items["overdue_items"].count()
            if hasattr(items["overdue_items"], "count")
            else len(items["overdue_items"])
        )
        pending_count = (
            items["pending_files"].count()
            if hasattr(items["pending_files"], "count")
            else len(items["pending_files"])
        )
        active_staff = (
            User.objects.filter(
                is_active=True,
            )
            .filter(
                Q(departments__head=department) | Q(units__department=department),
            )
            .distinct()
            .count()
        )
        workflow_instances = WorkflowInstance.objects.filter(
            initiated_by__in=User.objects.filter(
                is_active=True,
            ).filter(
                Q(departments__head=department) | Q(units__department=department),
            ),
            created_at__date=today,
        ).count()
        summary = {
            "success": True,
            "department": department.code,
            "department_name": department.name,
            "date": today.isoformat(),
            "mail_received": total_mails,
            "files_created": total_files,
            "files_completed": completed_files,
            "files_pending": pending_count,
            "files_overdue": overdue_count,
            "active_staff": active_staff,
            "workflow_instances": workflow_instances,
            "pending_mails": [
                {
                    "id": m.id,
                    "reference": m.reference_number,
                    "title": m.title,
                    "status": m.status,
                }
                for m in items["pending_mails"][:10]
            ],
            "overdue_items": [
                {
                    "id": f.id,
                    "file_number": f.file_number,
                    "title": f.title,
                    "priority": f.priority,
                    "current_holder": f.current_holder.get_full_name()
                    if f.current_holder
                    else None,
                    "expected_completion": (
                        f.expected_completion_date.isoformat()
                        if f.expected_completion_date
                        else None
                    ),
                }
                for f in items["overdue_items"][:10]
            ],
        }
        logger.info(
            f"Daily summary generated for {department.code}: "
            f"{total_mails} mails, {total_files} files, {overdue_count} overdue"
        )
        return summary

    @transaction.atomic
    def check_overdue_items(self, department_code=None):
        department = self._get_department(department_code)
        if department is None:
            return {"success": False, "error": "Department not found"}
        overdue_files = File.objects.filter(
            Q(assigned_department=department) | Q(department=department),
            expected_completion_date__lt=timezone.now().date(),
            status__in=["ACTIVE", "PENDING", "IN_TRANSIT", "UNDER_REVIEW"],
            escalation_status="NORMAL",
        ).select_related("current_holder", "created_by")
        escalated = 0
        notified = set()
        for file_obj in overdue_files:
            try:
                old_priority = file_obj.priority
                new_priority = FileMovementService.PRIORITY_ESCALATION.get(
                    old_priority, old_priority
                )
                file_obj.priority = new_priority
                file_obj.escalation_status = "ESCALATED"
                file_obj.escalation_reason = (
                    f"Auto-escalated by DepartmentAgent: "
                    f"deadline {file_obj.expected_completion_date} passed"
                )
                file_obj.escalated_at = timezone.now()
                file_obj.save(
                    update_fields=[
                        "priority",
                        "escalation_status",
                        "escalation_reason",
                        "escalated_at",
                        "updated_at",
                    ]
                )
                FileMovementService._add_timeline_entry(
                    file_obj,
                    file_obj.status,
                    file_obj.created_by
                    or User.objects.filter(role="SYSADMIN", is_active=True).first(),
                    "ESCALATED",
                    f"Auto-escalated by DepartmentAgent: deadline passed",
                )
                file_obj.save(update_fields=["status_timeline"])
                if (
                    file_obj.current_holder
                    and file_obj.current_holder_id not in notified
                ):
                    NotificationService.send_notification(
                        recipient=file_obj.current_holder,
                        subject=f"OVERDUE: File {file_obj.file_number}",
                        message=(
                            f"File '{file_obj.title}' ({file_obj.file_number}) is overdue.\n"
                            f"Deadline: {file_obj.expected_completion_date}\n"
                            f"Auto-escalated from {old_priority} to {new_priority}."
                        ),
                        file=file_obj,
                        notification_type="DEADLINE_REMINDER",
                        priority="URGENT",
                    )
                    notified.add(file_obj.current_holder_id)
                if department.head and department.head_id not in notified:
                    NotificationService.send_notification(
                        recipient=department.head,
                        subject=f"OVERDUE: File {file_obj.file_number} ({department.name})",
                        message=(
                            f"File '{file_obj.title}' ({file_obj.file_number}) in your "
                            f"department is overdue.\n"
                            f"Deadline: {file_obj.expected_completion_date}\n"
                            f"Current holder: {file_obj.current_holder.get_full_name() if file_obj.current_holder else 'N/A'}\n"
                            f"Auto-escalated from {old_priority} to {new_priority}."
                        ),
                        file=file_obj,
                        notification_type="DEADLINE_REMINDER",
                        priority="URGENT",
                    )
                    notified.add(department.head_id)
                escalated += 1
            except Exception as e:
                logger.error(f"Failed to escalate overdue file {file_obj.id}: {e}")
        today = timezone.now().date()
        overdue_mails = Document.objects.filter(
            Q(assigned_department=department) | Q(department=department),
            status="PENDING",
            correspondence__response_deadline__lt=today,
        ).select_related("created_by")
        overdue_mails_count = overdue_mails.count()
        if (
            department.head
            and overdue_mails_count > 0
            and department.head_id not in notified
        ):
            NotificationService.send_notification(
                recipient=department.head,
                subject=f"OVERDUE: {overdue_mails_count} mail(s) require response",
                message=(
                    f"There are {overdue_mails_count} overdue mail items in "
                    f"{department.name} that require response."
                ),
                notification_type="DEADLINE_REMINDER",
                priority="URGENT",
            )
        today = timezone.now().date()
        logger.info(
            f"Overdue check for {department.code}: "
            f"{escalated} files escalated, {overdue_mails_count} overdue mails"
        )
        return {
            "success": True,
            "department": department.code,
            "files_escalated": escalated,
            "overdue_mails": overdue_mails_count,
            "notified_users": len(notified),
        }

    def auto_route(self, item):
        try:
            if isinstance(item, File):
                return self.file_distributor.distribute(item)
            elif isinstance(item, Document):
                return self.mail_distributor.distribute(item)
            elif isinstance(item, dict):
                return self.mail_distributor.distribute(item)
            else:
                logger.warning(f"Unknown item type for auto_route: {type(item)}")
                return {
                    "success": False,
                    "error": f"Unsupported item type: {type(item)}",
                }
        except Exception as e:
            logger.error(f"Auto-route failed: {e}")
            return {"success": False, "error": str(e)}


class AutomationEngine:
    """Central orchestration engine for all automation tasks."""

    def __init__(self):
        self.router = AgenticRouter()
        self.mail_distributor = MailDistributor()
        self.file_distributor = FileDistributor()
        self._department_agents = {}

    def get_department_agent(self, department_code):
        if department_code not in self._department_agents:
            self._department_agents[department_code] = DepartmentAgent(department_code)
        return self._department_agents[department_code]

    def process_all_pending_items(self):
        results = {
            "mails": {"processed": 0, "errors": 0},
            "files": {"processed": 0, "errors": 0},
        }
        unassigned_mails = Document.objects.filter(
            assigned_department__isnull=True,
            status__in=["DRAFT", "PENDING"],
        ).select_related("created_by")[:100]
        for mail in unassigned_mails:
            try:
                self.mail_distributor.distribute(mail)
                results["mails"]["processed"] += 1
            except Exception as e:
                logger.error(f"Failed to process mail {mail.id}: {e}")
                results["mails"]["errors"] += 1
        unassigned_files = File.objects.filter(
            assigned_department__isnull=True,
            status__in=["DRAFT", "ACTIVE", "PENDING"],
            current_workflow_step__lte=1,
        ).select_related("created_by")[:100]
        for file_obj in unassigned_files:
            try:
                self.file_distributor.distribute(file_obj)
                results["files"]["processed"] += 1
            except Exception as e:
                logger.error(f"Failed to process file {file_obj.id}: {e}")
                results["files"]["errors"] += 1
        logger.info(
            f"Pending items processed: "
            f"mails={results['mails']['processed']}/{results['mails']['processed'] + results['mails']['errors']}, "
            f"files={results['files']['processed']}/{results['files']['processed'] + results['files']['errors']}"
        )
        return results

    def check_all_overdue_items(self):
        departments = Department.objects.filter(is_active=True)
        results = []
        for dept in departments:
            agent = self.get_department_agent(dept.code)
            result = agent.check_overdue_items(dept.code)
            results.append(result)
        total_escalated = sum(
            r.get("files_escalated", 0) for r in results if r.get("success")
        )
        logger.info(
            f"Overdue check complete: {total_escalated} files escalated across {len(results)} departments"
        )
        return {
            "departments_checked": len(results),
            "total_escalated": total_escalated,
            "details": results,
        }

    def generate_all_daily_summaries(self):
        departments = Department.objects.filter(is_active=True)
        summaries = []
        for dept in departments:
            agent = self.get_department_agent(dept.code)
            summary = agent.generate_daily_summary(dept.code)
            summaries.append(summary)
        logger.info(f"Daily summaries generated for {len(summaries)} departments")
        return summaries

    def rebalance_all_workloads(self):
        departments = Department.objects.filter(is_active=True)
        results = []
        for dept in departments:
            result = self.file_distributor.rebalance_workload(dept)
            results.append({"department": dept.code, **result})
        total_rebalanced = sum(
            r.get("rebalanced", 0) for r in results if r.get("success")
        )
        logger.info(f"Workload rebalance complete: {total_rebalanced} files moved")
        return {
            "departments_checked": len(results),
            "total_rebalanced": total_rebalanced,
            "details": results,
        }

    def run_full_cycle(self):
        logger.info("Starting full automation cycle")
        cycle_start = timezone.now()
        results = {
            "pending_items": self.process_all_pending_items(),
            "overdue_check": self.check_all_overdue_items(),
            "workload_rebalance": self.rebalance_all_workloads(),
            "daily_summaries": self.generate_all_daily_summaries(),
        }
        duration = (timezone.now() - cycle_start).total_seconds()
        logger.info(f"Full automation cycle completed in {duration:.2f} seconds")
        results["duration_seconds"] = duration
        return results


def run_automation():
    engine = AutomationEngine()
    return engine.run_full_cycle()


def process_pending_items():
    engine = AutomationEngine()
    return engine.process_all_pending_items()


def check_overdue():
    engine = AutomationEngine()
    return engine.check_all_overdue_items()


def rebalance_workloads():
    engine = AutomationEngine()
    return engine.rebalance_all_workloads()


def generate_daily_summaries():
    engine = AutomationEngine()
    return engine.generate_all_daily_summaries()
