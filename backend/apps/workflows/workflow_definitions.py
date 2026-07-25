"""
13-Step Workflow Definitions for E-File Movement & E-Registry
Based on Education District IV specification
"""

# 13-Step Incoming Mail Workflow
INCOMING_MAIL_WORKFLOW = {
    'name': 'Incoming Mail Processing',
    'description': '13-step workflow for processing incoming mail from receipt to archival',
    'steps': [
        {
            'order': 1,
            'name': 'Mail Receipt',
            'description': 'Physical mail received at mail room',
            'action': 'RECEIVED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 2,
            'name': 'Mail Registration',
            'description': 'Register mail in system with unique number',
            'action': 'REGISTERED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 3,
            'name': 'Mail Scanning',
            'description': 'Scan physical mail and attach digital copy',
            'action': 'SCANNED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 4,
            'name': 'Mail Classification',
            'description': 'Classify mail by priority, confidentiality, and type',
            'action': 'CLASSIFIED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 5,
            'name': 'Mail Sorting',
            'description': 'Sort mail by department and urgency',
            'action': 'SORTED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 6,
            'name': 'Department Assignment',
            'description': 'Assign mail to appropriate department head',
            'action': 'ASSIGNED',
            'required_role': 'TG',
        },
        {
            'order': 7,
            'name': 'Department Review',
            'description': 'Department head reviews and assigns to staff',
            'action': 'UNDER_REVIEW',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 8,
            'name': 'Staff Action',
            'description': 'Assigned staff takes required action',
            'action': 'IN_ACTION',
            'required_role': 'STAFF',
        },
        {
            'order': 9,
            'name': 'Response Preparation',
            'description': 'Prepare response or action report',
            'action': 'RESPONSE_PREPARED',
            'required_role': 'STAFF',
        },
        {
            'order': 10,
            'name': 'Supervisor Review',
            'description': 'Supervisor reviews response/action taken',
            'action': 'SUPERVISOR_REVIEW',
            'required_role': 'SUPERVISOR',
        },
        {
            'order': 11,
            'name': 'Final Approval',
            'description': 'Final approval for response dispatch',
            'action': 'APPROVED',
            'required_role': 'TG',
        },
        {
            'order': 12,
            'name': 'Response Dispatch',
            'description': 'Send response to sender',
            'action': 'DISPATCHED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 13,
            'name': 'Mail Archival',
            'description': 'Archive mail and update records',
            'action': 'ARCHIVED',
            'required_role': 'MAIL_ROOM',
        },
    ]
}

# 13-Step Outgoing Mail Workflow
OUTGOING_MAIL_WORKFLOW = {
    'name': 'Outgoing Mail Processing',
    'description': '13-step workflow for processing outgoing mail from draft to archival',
    'steps': [
        {
            'order': 1,
            'name': 'Draft Creation',
            'description': 'Create draft of outgoing mail',
            'action': 'DRAFT',
            'required_role': 'STAFF',
        },
        {
            'order': 2,
            'name': 'Content Review',
            'description': 'Review content for accuracy and completeness',
            'action': 'CONTENT_REVIEW',
            'required_role': 'STAFF',
        },
        {
            'order': 3,
            'name': 'Classification',
            'description': 'Classify mail by priority and confidentiality',
            'action': 'CLASSIFIED',
            'required_role': 'STAFF',
        },
        {
            'order': 4,
            'name': 'Department Head Review',
            'description': 'Department head reviews and approves content',
            'action': 'DEPT_HEAD_REVIEW',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 5,
            'name': 'TG Review',
            'description': 'Tutor General reviews for official correspondence',
            'action': 'TG_REVIEW',
            'required_role': 'TG',
        },
        {
            'order': 6,
            'name': 'Legal Review',
            'description': 'Legal review if required (contracts, agreements)',
            'action': 'LEGAL_REVIEW',
            'required_role': 'LEGAL',
        },
        {
            'order': 7,
            'name': 'Final Approval',
            'description': 'Final approval for dispatch',
            'action': 'APPROVED',
            'required_role': 'TG',
        },
        {
            'order': 8,
            'name': 'Mail Registration',
            'description': 'Register outgoing mail with unique number',
            'action': 'REGISTERED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 9,
            'name': 'Document Preparation',
            'description': 'Prepare physical documents for dispatch',
            'action': 'DOCUMENTS_READY',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 10,
            'name': 'Envelope Preparation',
            'description': 'Prepare envelope with proper addressing',
            'action': 'ENVELOPE_READY',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 11,
            'name': 'Mail Dispatch',
            'description': 'Dispatch mail via appropriate channel',
            'action': 'DISPATCHED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 12,
            'name': 'Delivery Confirmation',
            'description': 'Confirm delivery to recipient',
            'action': 'DELIVERED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 13,
            'name': 'Mail Archival',
            'description': 'Archive outgoing mail and update records',
            'action': 'ARCHIVED',
            'required_role': 'MAIL_ROOM',
        },
    ]
}

# 8-Step School-to-HQ Correspondence Workflow
SCHOOL_TO_HQ_WORKFLOW = {
    'name': 'School to HQ Correspondence',
    'description': '8-step workflow for school-to-HQ correspondence',
    'steps': [
        {
            'order': 1,
            'name': 'Draft Creation',
            'description': 'School staff creates correspondence draft',
            'action': 'DRAFT',
            'required_role': 'SCHOOL_STAFF',
        },
        {
            'order': 2,
            'name': 'Principal Review',
            'description': 'School principal reviews and approves',
            'action': 'PRINCIPAL_REVIEW',
            'required_role': 'PRINCIPAL',
        },
        {
            'order': 3,
            'name': 'Submission',
            'description': 'Submit to HQ department',
            'action': 'SUBMITTED',
            'required_role': 'PRINCIPAL',
        },
        {
            'order': 4,
            'name': 'HQ Receipt',
            'description': 'HQ department receives correspondence',
            'action': 'RECEIVED_AT_HQ',
            'required_role': 'HQ_STAFF',
        },
        {
            'order': 5,
            'name': 'Department Review',
            'description': 'HQ department reviews correspondence',
            'action': 'UNDER_REVIEW',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 6,
            'name': 'TG Approval',
            'description': 'Tutor General approval if required',
            'action': 'TG_APPROVAL',
            'required_role': 'TG',
        },
        {
            'order': 7,
            'name': 'Response/Action',
            'description': 'Prepare and send response or take action',
            'action': 'COMPLETED',
            'required_role': 'HQ_STAFF',
        },
        {
            'order': 8,
            'name': 'Archival',
            'description': 'Archive correspondence and notify school',
            'action': 'ARCHIVED',
            'required_role': 'HQ_STAFF',
        },
    ]
}

# 8-Step HQ-to-School Correspondence Workflow
HQ_TO_SCHOOL_WORKFLOW = {
    'name': 'HQ to School Correspondence',
    'description': '8-step workflow for HQ-to-school correspondence',
    'steps': [
        {
            'order': 1,
            'name': 'Draft Creation',
            'description': 'HQ staff creates correspondence draft',
            'action': 'DRAFT',
            'required_role': 'HQ_STAFF',
        },
        {
            'order': 2,
            'name': 'Department Review',
            'description': 'HQ department head reviews',
            'action': 'DEPT_REVIEW',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 3,
            'name': 'TG Approval',
            'description': 'Tutor General approval',
            'action': 'TG_APPROVAL',
            'required_role': 'TG',
        },
        {
            'order': 4,
            'name': 'Registration',
            'description': 'Register and assign reference number',
            'action': 'REGISTERED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 5,
            'name': 'Dispatch',
            'description': 'Dispatch to school(s)',
            'action': 'DISPATCHED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 6,
            'name': 'School Receipt',
            'description': 'School receives correspondence',
            'action': 'RECEIVED_AT_SCHOOL',
            'required_role': 'SCHOOL_STAFF',
        },
        {
            'order': 7,
            'name': 'Principal Action',
            'description': 'Principal reviews and takes action',
            'action': 'PRINCIPAL_ACTION',
            'required_role': 'PRINCIPAL',
        },
        {
            'order': 8,
            'name': 'Acknowledgement',
            'description': 'Send acknowledgement to HQ and archive',
            'action': 'ACKNOWLEDGED',
            'required_role': 'SCHOOL_STAFF',
        },
    ]
}

# 9-Step Internal Memo/Circular Workflow
INTERNAL_MEMO_WORKFLOW = {
    'name': 'Internal Memo/Circular',
    'description': '9-step workflow for internal memos and circulars',
    'steps': [
        {
            'order': 1,
            'name': 'Draft Creation',
            'description': 'Create memo/circular draft',
            'action': 'DRAFT',
            'required_role': 'STAFF',
        },
        {
            'order': 2,
            'name': 'Content Review',
            'description': 'Review content for accuracy',
            'action': 'CONTENT_REVIEW',
            'required_role': 'STAFF',
        },
        {
            'order': 3,
            'name': 'Classification',
            'description': 'Classify by priority and confidentiality',
            'action': 'CLASSIFIED',
            'required_role': 'STAFF',
        },
        {
            'order': 4,
            'name': 'Department Head Review',
            'description': 'Department head reviews and approves',
            'action': 'DEPT_HEAD_REVIEW',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 5,
            'name': 'TG Approval',
            'description': 'Tutor General approval for official memos',
            'action': 'TG_APPROVAL',
            'required_role': 'TG',
        },
        {
            'order': 6,
            'name': 'Registration',
            'description': 'Register and assign reference number',
            'action': 'REGISTERED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 7,
            'name': 'Circulation',
            'description': 'Circulate to intended recipients',
            'action': 'CIRCULATED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 8,
            'name': 'Acknowledgement',
            'description': 'Recipients acknowledge receipt',
            'action': 'ACKNOWLEDGED',
            'required_role': 'RECIPIENT',
        },
        {
            'order': 9,
            'name': 'Archival',
            'description': 'Archive memo/circular',
            'action': 'ARCHIVED',
            'required_role': 'MAIL_ROOM',
        },
    ]
}

# 8-Step Department-to-Department Workflow
DEPARTMENT_TO_DEPARTMENT_WORKFLOW = {
    'name': 'Department-to-Department',
    'description': '8-step workflow for inter-department correspondence',
    'steps': [
        {
            'order': 1,
            'name': 'Draft Creation',
            'description': 'Create inter-department correspondence',
            'action': 'DRAFT',
            'required_role': 'STAFF',
        },
        {
            'order': 2,
            'name': 'Department Head Approval',
            'description': 'Source department head approves',
            'action': 'DEPT_HEAD_APPROVAL',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 3,
            'name': 'Registration',
            'description': 'Register and assign reference number',
            'action': 'REGISTERED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 4,
            'name': 'Dispatch',
            'description': 'Dispatch to target department',
            'action': 'DISPATCHED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 5,
            'name': 'Department Receipt',
            'description': 'Target department receives correspondence',
            'action': 'RECEIVED',
            'required_role': 'DEPT_STAFF',
        },
        {
            'order': 6,
            'name': 'Department Review',
            'description': 'Target department reviews and assigns',
            'action': 'UNDER_REVIEW',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 7,
            'name': 'Action/Response',
            'description': 'Take required action or prepare response',
            'action': 'COMPLETED',
            'required_role': 'DEPT_STAFF',
        },
        {
            'order': 8,
            'name': 'Archival',
            'description': 'Archive correspondence',
            'action': 'ARCHIVED',
            'required_role': 'MAIL_ROOM',
        },
    ]
}

# File Movement Workflow (13 steps as per spec)
FILE_MOVEMENT_WORKFLOW = {
    'name': 'File Movement',
    'description': '13-step workflow for file movement and tracking',
    'steps': [
        {
            'order': 1,
            'name': 'File Creation',
            'description': 'Create file with unique number',
            'action': 'CREATED',
            'required_role': 'CREATOR',
        },
        {
            'order': 2,
            'name': 'File Registration',
            'description': 'Register file in system',
            'action': 'REGISTERED',
            'required_role': 'REGISTRAR',
        },
        {
            'order': 3,
            'name': 'Classification',
            'description': 'Classify file by category and security level',
            'action': 'CLASSIFIED',
            'required_role': 'CREATOR',
        },
        {
            'order': 4,
            'name': 'Department Assignment',
            'description': 'Assign to appropriate department',
            'action': 'ASSIGNED',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 5,
            'name': 'Initial Review',
            'description': 'Initial review by department head',
            'action': 'INITIAL_REVIEW',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 6,
            'name': 'Processing',
            'description': 'File processed by assigned staff',
            'action': 'PROCESSING',
            'required_role': 'STAFF',
        },
        {
            'order': 7,
            'name': 'Supervisor Review',
            'description': 'Supervisor reviews processing',
            'action': 'SUPERVISOR_REVIEW',
            'required_role': 'SUPERVISOR',
        },
        {
            'order': 8,
            'name': 'Department Approval',
            'description': 'Department head approves',
            'action': 'DEPT_APPROVAL',
            'required_role': 'DEPT_HEAD',
        },
        {
            'order': 9,
            'name': 'TG/PS Review',
            'description': 'TG/PS review for official files',
            'action': 'TG_REVIEW',
            'required_role': 'TG',
        },
        {
            'order': 10,
            'name': 'Final Approval',
            'description': 'Final approval from TG/PS',
            'action': 'FINAL_APPROVAL',
            'required_role': 'TG',
        },
        {
            'order': 11,
            'name': 'Dispatch/Return',
            'description': 'Dispatch to destination or return to creator',
            'action': 'DISPATCHED',
            'required_role': 'MAIL_ROOM',
        },
        {
            'order': 12,
            'name': 'Receipt Confirmation',
            'description': 'Confirm receipt at destination',
            'action': 'RECEIVED',
            'required_role': 'RECIPIENT',
        },
        {
            'order': 13,
            'name': 'File Archival',
            'description': 'Archive completed file',
            'action': 'ARCHIVED',
            'required_role': 'MAIL_ROOM',
        },
    ]
}

# Department Codes
DEPARTMENT_CODES = {
    'TG': 'Tutor General',
    'HR': 'Human Resources',
    'FIN': 'Finance',
    'AUD': 'Audit',
    'QA': 'Quality Assurance',
    'CC': 'Curriculum Center',
    'FRE': 'French',
    'EMIS': 'Education Management Information System',
    'PLAN': 'Planning',
    'PROC': 'Procurement',
    'PA': 'Public Affairs',
    'SA': 'Student Affairs',
    'REG': 'Registry',
}

# File Categories
FILE_CATEGORIES = {
    'ADMIN': 'Administrative',
    'ACAD': 'Academic',
    'FIN': 'Finance',
    'INSP': 'Inspection',
    'DISC': 'Discipline',
    'COCC': 'Co-curricular',
    'POL': 'Policy',
    'CORR': 'Correspondence',
    'PROC': 'Procurement',
}

# Security Classifications
SECURITY_CLASSIFICATIONS = {
    'PUBLIC': 'Public',
    'CONFIDENTIAL': 'Confidential',
    'RESTRICTED': 'Restricted',
    'TOP_SECRET': 'Top Secret',
}

# Workflow Step Statuses
WORKFLOW_STEP_STATUSES = {
    'PENDING': 'Pending',
    'IN_PROGRESS': 'In Progress',
    'COMPLETED': 'Completed',
    'BLOCKED': 'Blocked',
    'SKIPPED': 'Skipped',
    'REJECTED': 'Rejected',
}

# Mail Number Formats
MAIL_NUMBER_FORMATS = {
    'INCOMING': 'EDIV/MAIL/{year}/{seq:04d}',
    'OUTGOING': 'EDIV/OUT/{year}/{seq:04d}',
    'SCHOOL_TO_HQ': 'EDIV/S2H/{year}/{seq:04d}',
    'HQ_TO_SCHOOL': 'EDIV/H2S/{year}/{seq:04d}',
    'INTERNAL': 'EDIV/INT/{year}/{seq:04d}',
    'DEPARTMENT': 'EDIV/DEPT/{year}/{seq:04d}',
}

# File Number Format
FILE_NUMBER_FORMAT = 'EDIV-{year}-{dept_code}-{seq:04d}'

# All Workflow Definitions
ALL_WORKFLOWS = {
    'INCOMING_MAIL': INCOMING_MAIL_WORKFLOW,
    'OUTGOING_MAIL': OUTGOING_MAIL_WORKFLOW,
    'SCHOOL_TO_HQ': SCHOOL_TO_HQ_WORKFLOW,
    'HQ_TO_SCHOOL': HQ_TO_SCHOOL_WORKFLOW,
    'INTERNAL_MEMO': INTERNAL_MEMO_WORKFLOW,
    'DEPARTMENT_TO_DEPARTMENT': DEPARTMENT_TO_DEPARTMENT_WORKFLOW,
    'FILE_MOVEMENT': FILE_MOVEMENT_WORKFLOW,
}


def get_workflow(workflow_type):
    """Get workflow definition by type."""
    return ALL_WORKFLOWS.get(workflow_type)


def get_workflow_steps(workflow_type):
    """Get steps for a specific workflow type."""
    workflow = get_workflow(workflow_type)
    if workflow:
        return workflow['steps']
    return []


def get_step_by_order(workflow_type, order):
    """Get a specific step by order number."""
    steps = get_workflow_steps(workflow_type)
    for step in steps:
        if step['order'] == order:
            return step
    return None


def get_next_step(workflow_type, current_order):
    """Get the next step in workflow."""
    return get_step_by_order(workflow_type, current_order + 1)


def get_previous_step(workflow_type, current_order):
    """Get the previous step in workflow."""
    if current_order > 1:
        return get_step_by_order(workflow_type, current_order - 1)
    return None


def get_workflow_status(current_order, total_steps):
    """Calculate workflow progress percentage."""
    if total_steps == 0:
        return 0
    return round((current_order / total_steps) * 100, 2)
