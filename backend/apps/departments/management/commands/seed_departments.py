from django.core.management.base import BaseCommand
from apps.departments.models import Department, Unit


# --- DEPARTMENTS (actual departments only) ---
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
            {'name': 'Science & Technology Unit', 'code': 'CCP_STE', 'description': 'Coordinates science fairs, robotics, STEM clubs, and technology competitions across schools.'},
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
        'name': 'Registry Department',
        'code': 'REG',
        'category': 'CORE',
        'description': 'Manages official records, correspondence, filing, and administrative documentation for the district.',
        'units': [
            {'name': 'Records Management Unit', 'code': 'RGP_RCR', 'description': 'Manages filing systems, archiving, and document retrieval.'},
            {'name': 'Correspondence Unit', 'code': 'RGP_COR', 'description': 'Handles incoming and outgoing official correspondence.'},
        ],
    },
    {
        'name': 'Special Duties Department',
        'code': 'SPD',
        'category': 'CORE',
        'description': 'Handles special assignments, inter-agency liaison, and ad-hoc tasks as directed by the Tutor General.',
        'units': [
            {'name': 'Inter-Agency Liaison Unit', 'code': 'SDP_LIA', 'description': 'Coordinates liaison with external agencies and government bodies.'},
            {'name': 'Special Projects Unit', 'code': 'SDP_PRJ', 'description': 'Manages special projects and task-force assignments.'},
        ],
    },
    {
        'name': 'School Support Services Department',
        'code': 'SSS',
        'category': 'SUPPORT',
        'description': 'Provides technical support, mentoring, and capacity building for schools in the district.',
        'units': [
            {'name': 'School Mentoring Unit', 'code': 'SSP_MNT', 'description': 'Provides mentoring and advisory support to school administrators.'},
            {'name': 'Resource Centre Unit', 'code': 'SSP_RES', 'description': 'Manages teaching resources, learning materials, and resource centres.'},
            {'name': 'School Improvement Unit', 'code': 'SSP_IMP', 'description': 'Develops and monitors school improvement plans.'},
        ],
    },
    {
        'name': 'French Language Department',
        'code': 'FRENCH',
        'category': 'SUPPORT',
        'description': 'Coordinates French language instruction, examinations, and francophone educational partnerships.',
        'units': [
            {'name': 'French Instruction Unit', 'code': 'FRP_INS', 'description': 'Manages French language teaching and teacher deployment.'},
            {'name': 'French Examinations Unit', 'code': 'FRP_EXM', 'description': 'Coordinates French language examinations and certifications.'},
        ],
    },
]


# --- MAJOR UNITS (District Headquarters level, not under any department) ---
MAJOR_UNITS = [
    {
        'name': 'Internal Audit Unit',
        'code': 'AUDIT',
        'description': 'Provides independent assurance on internal controls, compliance, and governance processes across the district.',
    },
    {
        'name': 'Education Management Information System (EMIS) Unit',
        'code': 'EMIS',
        'description': 'Manages data collection, analysis, and reporting for evidence-based educational planning and decision-making.',
    },
    {
        'name': 'Planning, Research & Statistics Unit',
        'code': 'PLAN',
        'description': 'Drives strategic planning, educational research, and statistical analysis for the district.',
    },
    {
        'name': 'Procurement Unit',
        'code': 'PROC',
        'description': 'Manages procurement processes, vendor relations, and supply chain in line with due process requirements.',
    },
    {
        'name': 'Public Affairs Unit',
        'code': 'PA',
        'description': 'Manages public relations, media, communications, and community engagement for the district.',
    },
]


class Command(BaseCommand):
    help = 'Seed Education District IV departments, major units, and their sub-units'

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
                    code=unit_data['code'],
                    defaults={**unit_data, 'department': dept},
                )
                if u_created:
                    unit_created += 1
                else:
                    unit_skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'  Departments: {dept_created} created, {dept_skipped} skipped | '
            f'Sub-units: {unit_created} created, {unit_skipped} skipped'
        ))

        # --- Major Units (District HQ level) ---
        self.stdout.write(self.style.NOTICE('\nSeeding major district units...'))

        major_created = 0
        major_skipped = 0

        for unit_data in MAJOR_UNITS:
            unit, created = Unit.objects.get_or_create(
                code=unit_data['code'],
                defaults={**unit_data, 'department': None},
            )
            if created:
                major_created += 1
                self.stdout.write(f'  + Major Unit: {unit.name}')
            else:
                major_skipped += 1
                self.stdout.write(f'  ~ Exists: {unit.name}')

        self.stdout.write(self.style.SUCCESS(
            f'  Major Units: {major_created} created, {major_skipped} skipped'
        ))

        self.stdout.write(self.style.SUCCESS('\nAll seeding complete!'))
