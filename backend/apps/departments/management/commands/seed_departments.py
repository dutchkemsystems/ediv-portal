from django.core.management.base import BaseCommand
from apps.departments.models import Department, Unit


DEPARTMENTS = [
    {
        'name': 'Administration & Human Resources Department',
        'code': 'ADMIN_HR',
        'category': 'CORE',
        'description': 'Handles recruitment, payroll, staff training, welfare, and all human resource management functions for the district.',
        'units': [
            {'name': 'Recruitment Unit', 'code': 'ADM_REC', 'description': 'Handles recruitment, onboarding, and staff placement processes.'},
            {'name': 'Payroll Unit', 'code': 'ADM_PAY', 'description': 'Manages salary computation, payments, and remittances.'},
            {'name': 'Training Unit', 'code': 'ADM_TRN', 'description': 'Coordinates staff training, workshops, and capacity building programmes.'},
            {'name': 'Staff Welfare Unit', 'code': 'ADM_WEL', 'description': 'Manages staff welfare schemes, housing, and cooperative matters.'},
        ],
    },
    {
        'name': 'Finance Department',
        'code': 'FIN',
        'category': 'CORE',
        'description': 'Manages budgeting, accounting, financial reporting, and fiscal planning for the district.',
        'units': [
            {'name': 'Budget Unit', 'code': 'FIN_BUD', 'description': 'Prepares and monitors district budgets.'},
            {'name': 'Accounts Unit', 'code': 'FIN_ACC', 'description': 'Handles day-to-day accounting, bookkeeping, and financial records.'},
            {'name': 'Revenue Unit', 'code': 'FIN_REV', 'description': 'Manages internally generated revenue collection and reporting.'},
        ],
    },
    {
        'name': 'Internal Audit Department',
        'code': 'AUDIT',
        'category': 'CORE',
        'description': 'Provides independent assurance on internal controls, compliance, and governance processes.',
        'units': [
            {'name': 'Compliance Audit Unit', 'code': 'AUP_CMP', 'description': 'Audits compliance with policies, laws, and regulations.'},
            {'name': 'Operational Audit Unit', 'code': 'AUP_OPS', 'description': 'Reviews operational efficiency and effectiveness of departmental processes.'},
        ],
    },
    {
        'name': 'Quality Assurance Department',
        'code': 'QA',
        'category': 'CORE',
        'description': 'Ensures quality standards in teaching, learning, and educational service delivery across the district.',
        'units': [
            {'name': 'Standards & Inspection Unit', 'code': 'QAP_STD', 'description': 'Sets educational standards and conducts school inspections.'},
            {'name': 'Curriculum Review Unit', 'code': 'QAP_CRV', 'description': 'Reviews and monitors curriculum implementation across schools.'},
        ],
    },
    {
        'name': 'Co-Curricular Activities Department',
        'code': 'CC',
        'category': 'CORE',
        'description': 'Coordinates sports, clubs, competitions, and extracurricular programmes across schools.',
        'units': [
            {'name': 'Sports Unit', 'code': 'CCP_SPT', 'description': 'Organises inter-school sports competitions and athletic programmes.'},
            {'name': 'Clubs & Societies Unit', 'code': 'CCP_CLB', 'description': 'Manages school clubs, societies, and cultural activities.'},
            {'name': 'Debate & Quiz Unit', 'code': 'CCP_DBT', 'description': 'Coordinates inter-school debates, quiz, and academic competitions.'},
        ],
    },
    {
        'name': 'Education Management Information System Department',
        'code': 'EMIS',
        'category': 'CORE',
        'description': 'Manages data collection, analysis, and reporting for evidence-based educational planning.',
        'units': [
            {'name': 'Data Collection Unit', 'code': 'EMP_DCL', 'description': 'Collects and validates school data from all institutions.'},
            {'name': 'Analytics & Reporting Unit', 'code': 'EMP_ANR', 'description': 'Analyses educational data and produces reports for decision-making.'},
            {'name': 'ICT Support Unit', 'code': 'EMP_ICT', 'description': 'Provides technical support for ICT infrastructure and digital tools.'},
        ],
    },
    {
        'name': 'Planning, Research & Statistics Department',
        'code': 'PLAN',
        'category': 'CORE',
        'description': 'Drives strategic planning, educational research, and statistical analysis for the district.',
        'units': [
            {'name': 'Strategic Planning Unit', 'code': 'PLP_STP', 'description': 'Develops and monitors the district strategic plan.'},
            {'name': 'Research Unit', 'code': 'PLP_RES', 'description': 'Conducts educational research and evaluation studies.'},
            {'name': 'Statistics Unit', 'code': 'PLP_STA', 'description': 'Manages statistical data and demographic analysis.'},
        ],
    },
    {
        'name': 'Procurement Department',
        'code': 'PROC',
        'category': 'CORE',
        'description': 'Manages procurement processes, vendor relations, and supply chain in line with due process requirements.',
        'units': [
            {'name': 'Tender & Contracts Unit', 'code': 'PRP_TND', 'description': 'Handles tendering, bidding, and contract management.'},
            {'name': 'Supply Chain Unit', 'code': 'PRP_SCP', 'description': 'Manages inventory, logistics, and distribution of materials.'},
        ],
    },
    {
        'name': 'Public Affairs Department',
        'code': 'PA',
        'category': 'CORE',
        'description': 'Manages public relations, media, communications, and community engagement for the district.',
        'units': [
            {'name': 'Media & Publicity Unit', 'code': 'PAP_MED', 'description': 'Handles press releases, media relations, and publicity.'},
            {'name': 'Community Engagement Unit', 'code': 'PAP_CEG', 'description': 'Coordinates community outreach and stakeholder engagement.'},
        ],
    },
    {
        'name': 'Schools Administration Department',
        'code': 'SA',
        'category': 'CORE',
        'description': 'Oversees the day-to-day administration of all secondary schools in the district.',
        'units': [
            {'name': 'School Inspection Unit', 'code': 'SAP_INS', 'description': 'Conducts routine inspections and monitoring of schools.'},
            {'name': 'Enrolment & Placement Unit', 'code': 'SAP_ENP', 'description': 'Manages student enrolment, transfers, and placement.'},
            {'name': 'School Records Unit', 'code': 'SAP_RCR', 'description': 'Maintains school records, certificates, and documentation.'},
        ],
    },
    {
        'name': 'French Unit',
        'code': 'FRENCH',
        'category': 'SUPPORT',
        'description': 'Coordinates French language instruction, examinations, and francophone educational partnerships.',
        'units': [
            {'name': 'French Instruction Unit', 'code': 'FRP_INS', 'description': 'Manages French language teaching and teacher deployment.'},
            {'name': 'French Examinations Unit', 'code': 'FRP_EXM', 'description': 'Coordinates French language examinations and certifications.'},
        ],
    },
    {
        'name': 'Registry Department',
        'code': 'REG',
        'category': 'CORE',
        'description': 'Manages official records, correspondence, filing, and administrative documentation for the district.',
        'units': [
            {'name': 'Records Management Unit', 'code': 'RGP_RCR', 'description': 'Manages filing systems, archiving, and document retrieval.'},
            {'name': 'Correspondence Unit', 'code': 'RGP_COR', 'description': 'Handles incoming and outgoing official correspondence.'},
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed Education District IV departments and their units'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding departments...'))

        dept_created = 0
        dept_skipped = 0
        unit_created = 0
        unit_skipped = 0

        for dept_data in DEPARTMENTS:
            units_data = dept_data.pop('units')
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data,
            )
            if created:
                dept_created += 1
                self.stdout.write(f'  + Department: {dept.name}')
            else:
                dept_skipped += 1
                self.stdout.write(f'  ~ Exists: {dept.name}')

            for unit_data in units_data:
                unit, u_created = Unit.objects.get_or_create(
                    department=dept,
                    code=unit_data['code'],
                    defaults=unit_data,
                )
                if u_created:
                    unit_created += 1
                else:
                    unit_skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Departments: {dept_created} created, {dept_skipped} skipped | '
            f'Units: {unit_created} created, {unit_skipped} skipped'
        ))
