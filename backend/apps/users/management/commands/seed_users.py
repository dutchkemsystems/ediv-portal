import random
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


# ---------------------------------------------------------------------------
# Admin / Head Office users
# ---------------------------------------------------------------------------

ADMIN_USERS = [
    {
        'email': 'admin@ediv.gov.ng',
        'first_name': 'System',
        'last_name': 'Administrator',
        'role': 'SYSADMIN',
        'password': 'Admin@12345678',
        'phone_number': '+2348010000001',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'email': 'tg@ediv.gov.ng',
        'first_name': 'Abimbola',
        'last_name': 'Adesanya',
        'role': 'TG',
        'password': 'TutorGen@12345',
        'phone_number': '+2348010000002',
        'is_staff': True,
        'is_superuser': False,
    },
    {
        'email': 'hr@ediv.gov.ng',
        'first_name': 'Funmilayo',
        'last_name': 'Ogundimu',
        'role': 'HR',
        'password': 'DeptHead@12345',
        'phone_number': '+2348010000003',
        'is_staff': True,
        'is_superuser': False,
    },
    {
        'email': 'finance@ediv.gov.ng',
        'first_name': 'Adewale',
        'last_name': 'Bakare',
        'role': 'FIN',
        'password': 'DeptHead@12345',
        'phone_number': '+2348010000004',
        'is_staff': True,
        'is_superuser': False,
    },
]


# ---------------------------------------------------------------------------
# Sample school data: 95 schools with principals, vice-principals, teachers
# ---------------------------------------------------------------------------

FIRST_NAMES_M = [
    'Oluwaseun', 'Adewale', 'Chinedu', 'Ibrahim', 'Oluwadamilola',
    'Emeka', 'Tunde', 'Kolade', 'Babatunde', 'Femi',
    'Sunday', 'Yemi', 'Kayode', 'Obinna', 'Segun',
    'Blessing', 'Akin', 'Dare', 'Nosa', 'Gbenga',
]

FIRST_NAMES_F = [
    'Aderonke', 'Folake', 'Chioma', 'Amina', 'Oluwabunmi',
    'Ngozi', 'Funke', 'Bukola', 'Adaeze', 'Halima',
    'Titilayo', 'Yetunde', 'Amara', 'Kemi', 'Ifeoma',
    'Blessing', 'Olayinka', 'Tolu', 'Nneka', 'Grace',
]

LAST_NAMES = [
    'Adeyemi', 'Ogundimu', 'Nwosu', 'Abubakar', 'Bakare',
    'Eze', 'Adesanya', 'Okafor', 'Lawal', 'Olumide',
    'Ibrahim', 'Akande', 'Chukwu', 'Bello', 'Fashola',
    'Onwueme', 'Tinubu', 'Obi', 'Aliyu', 'Ogunleye',
    'Ajayi', 'Amadi', 'Mohammed', 'Olaniyan', 'Igwe',
    'Adeleke', 'Osagie', 'Uche', 'Olawale', 'Akinola',
]

MALE_NAMES = FIRST_NAMES_M
FEMALE_NAMES = FIRST_NAMES_F


class Command(BaseCommand):
    help = 'Seed Education District IV admin users, sample school staff, and students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-students',
            action='store_true',
            help='Also create sample student accounts (requires schools to be seeded first)',
        )

    def handle(self, *args, **options):
        random.seed(42)

        # --- Admin / Head Office Users ---
        self.stdout.write(self.style.NOTICE('\n--- Seeding admin users ---'))
        admin_created = 0
        admin_skipped = 0
        for data in ADMIN_USERS:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                    'phone_number': data['phone_number'],
                    'is_staff': data.get('is_staff', False),
                    'is_superuser': data.get('is_superuser', False),
                },
            )
            if created:
                user.set_password(data['password'])
                user.save()
                admin_created += 1
                self.stdout.write(f'  + Admin: {user.email} ({user.role})')
            else:
                admin_skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'  Admin users: {admin_created} created, {admin_skipped} skipped'
        ))

        # --- Sample School Staff (Principals, VPs, Teachers) ---
        self.stdout.write(self.style.NOTICE('\n--- Seeding school staff ---'))
        staff_created = 0
        staff_skipped = 0

        from apps.schools.models import School
        schools = list(School.objects.all())
        if not schools:
            self.stdout.write(self.style.WARNING(
                '  No schools found. Run seed_schools command first. Skipping staff seeding.'
            ))
            return

        teacher_idx = 0
        for school in schools:
            # Create Principal
            is_male = random.choice([True, False])
            gender = 'M' if is_male else 'F'
            first_name = random.choice(MALE_NAMES if is_male else FEMALE_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = f'principal_{school.code.lower()}@ediv.gov.ng'

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'PRI',
                    'phone_number': f'+234802{random.randint(1000000, 9999999):07d}',
                },
            )
            if created:
                user.set_password('SchoolStaff@12345')
                user.save()
                school.principal = user
                school.save()
                staff_created += 1
            else:
                staff_skipped += 1

            # Create Vice Principal
            is_male2 = not is_male
            gender2 = 'M' if is_male2 else 'F'
            first_name2 = random.choice(MALE_NAMES if is_male2 else FEMALE_NAMES)
            last_name2 = random.choice(LAST_NAMES)
            email2 = f'vp_{school.code.lower()}@ediv.gov.ng'

            user2, created2 = User.objects.get_or_create(
                email=email2,
                defaults={
                    'first_name': first_name2,
                    'last_name': last_name2,
                    'role': 'VP',
                    'phone_number': f'+234803{random.randint(1000000, 9999999):07d}',
                },
            )
            if created2:
                user2.set_password('SchoolStaff@12345')
                user2.save()
                school.vice_principal = user2
                school.save()
                staff_created += 1
            else:
                staff_skipped += 1

            # Create 3-5 teachers per school
            num_teachers = random.randint(3, 5)
            for i in range(num_teachers):
                teacher_idx += 1
                is_male_t = random.choice([True, False])
                first_t = random.choice(MALE_NAMES if is_male_t else FEMALE_NAMES)
                last_t = random.choice(LAST_NAMES)
                email_t = f'teacher_{teacher_idx:04d}@ediv.gov.ng'

                user_t, created_t = User.objects.get_or_create(
                    email=email_t,
                    defaults={
                        'first_name': first_t,
                        'last_name': last_t,
                        'role': 'TCH',
                        'phone_number': f'+234804{random.randint(1000000, 9999999):07d}',
                    },
                )
                if created_t:
                    user_t.set_password('Teacher@12345')
                    user_t.save()
                    staff_created += 1
                else:
                    staff_skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'  School staff: {staff_created} created, {staff_skipped} skipped'
        ))

        # --- Sample Students ---
        if options['with_students']:
            self.stdout.write(self.style.NOTICE('\n--- Seeding sample students ---'))
            student_created = 0
            student_skipped = 0
            student_idx = 0

            for school in schools:
                # 2-4 students per school
                num_students = random.randint(2, 4)
                for i in range(num_students):
                    student_idx += 1
                    is_male_s = random.choice([True, False])
                    first_s = random.choice(MALE_NAMES if is_male_s else FEMALE_NAMES)
                    last_s = random.choice(LAST_NAMES)
                    email_s = f'student_{student_idx:04d}@student.ediv.gov.ng'

                    user_s, created_s = User.objects.get_or_create(
                        email=email_s,
                        defaults={
                            'first_name': first_s,
                            'last_name': last_s,
                            'role': 'STD',
                            'phone_number': '',
                        },
                    )
                    if created_s:
                        user_s.set_password('Student@12345')
                        user_s.save()
                        student_created += 1
                    else:
                        student_skipped += 1

            self.stdout.write(self.style.SUCCESS(
                f'  Students: {student_created} created, {student_skipped} skipped'
            ))

        self.stdout.write(self.style.SUCCESS('\nAll seeding complete!'))
