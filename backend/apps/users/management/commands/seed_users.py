import os
import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

DEFAULT_PASSWORDS = {
    "ADMIN_PASSWORD": "Admin@12345678",
    "TG_PASSWORD": "TutorGen@12345",
    "HEAD_OFFICE_PASSWORD": "HeadOffice@123",
    "SCHOOL_STAFF_PASSWORD": "SchoolStaff@12345",
    "TEACHER_PASSWORD": "Teacher@12345",
    "STUDENT_PASSWORD": "Student@12345",
}


def _get_password(key):
    return os.environ.get(key) or DEFAULT_PASSWORDS.get(key, "ChangeMe@123")


ADMIN_PASSWORD = _get_password("ADMIN_PASSWORD")
TG_PASSWORD = _get_password("TG_PASSWORD")
HEAD_OFFICE_PASSWORD = _get_password("HEAD_OFFICE_PASSWORD")
SCHOOL_STAFF_PASSWORD = _get_password("SCHOOL_STAFF_PASSWORD")
TEACHER_PASSWORD = _get_password("TEACHER_PASSWORD")
STUDENT_PASSWORD = _get_password("STUDENT_PASSWORD")


# ---------------------------------------------------------------------------
# Admin / Head Office users
# ---------------------------------------------------------------------------

ADMIN_USERS = [
    {
        "email": "admin@ediv.gov.ng",
        "first_name": "System",
        "last_name": "Administrator",
        "role": "SYSADMIN",
        "password": ADMIN_PASSWORD,
        "phone_number": "+2348010000001",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "tg.ps@ediv.gov.ng",
        "first_name": "Abimbola",
        "last_name": "Adesanya",
        "role": "TG_PS",
        "password": TG_PASSWORD,
        "phone_number": "+2348010000002",
        "is_staff": True,
        "is_superuser": False,
    },
]

# ---------------------------------------------------------------------------
# Department Heads (9 departments)
# ---------------------------------------------------------------------------

DEPARTMENT_HEADS = [
    {
        "email": "hr.head@ediv.gov.ng",
        "first_name": "Funmilayo",
        "last_name": "Ogundimu",
        "role": "HR",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000003",
        "department_code": "ADMIN_HR",
    },
    {
        "email": "finance.head@ediv.gov.ng",
        "first_name": "Adewale",
        "last_name": "Bakare",
        "role": "FIN",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000004",
        "department_code": "FIN",
    },
    {
        "email": "qa.head@ediv.gov.ng",
        "first_name": "Oluwaseun",
        "last_name": "Ajayi",
        "role": "QA",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000005",
        "department_code": "QA",
    },
    {
        "email": "cc.head@ediv.gov.ng",
        "first_name": "Chinedu",
        "last_name": "Eze",
        "role": "CC",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000006",
        "department_code": "CC",
    },
    {
        "email": "sa.head@ediv.gov.ng",
        "first_name": "Adewale",
        "last_name": "Lawal",
        "role": "SA",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000007",
        "department_code": "SA",
    },
    {
        "email": "registry.head@ediv.gov.ng",
        "first_name": "Folake",
        "last_name": "Okafor",
        "role": "REG",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000008",
        "department_code": "REG",
    },
    {
        "email": "spd.head@ediv.gov.ng",
        "first_name": "Ibrahim",
        "last_name": "Abubakar",
        "role": "SPD",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000009",
        "department_code": "SPD",
    },
    {
        "email": "sss.head@ediv.gov.ng",
        "first_name": "Ngozi",
        "last_name": "Nwosu",
        "role": "QA",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000010",
        "department_code": "SSS",
        "note": "SSS shares QA role - no dedicated SSS role in system",
    },
    {
        "email": "french.head@ediv.gov.ng",
        "first_name": "Amina",
        "last_name": "Mohammed",
        "role": "FRENCH",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000011",
        "department_code": "FRENCH",
    },
]

# ---------------------------------------------------------------------------
# Major Unit Heads (5 standalone district units)
# ---------------------------------------------------------------------------

UNIT_HEADS = [
    {
        "email": "audit.head@ediv.gov.ng",
        "first_name": "Tunde",
        "last_name": "Fashola",
        "role": "AUDIT",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000012",
        "unit_code": "AUDIT",
    },
    {
        "email": "emis.head@ediv.gov.ng",
        "first_name": "Kolade",
        "last_name": "Akande",
        "role": "EMIS",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000013",
        "unit_code": "EMIS",
    },
    {
        "email": "plan.head@ediv.gov.ng",
        "first_name": "Babatunde",
        "last_name": "Olumide",
        "role": "PLAN",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000014",
        "unit_code": "PLAN",
    },
    {
        "email": "procurement.head@ediv.gov.ng",
        "first_name": "Emeka",
        "last_name": "Chukwu",
        "role": "PROC",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000015",
        "unit_code": "PROC",
    },
    {
        "email": "pa.head@ediv.gov.ng",
        "first_name": "Funke",
        "last_name": "Bakare",
        "role": "PA",
        "password": HEAD_OFFICE_PASSWORD,
        "phone_number": "+2348010000016",
        "unit_code": "PA",
    },
]


# ---------------------------------------------------------------------------
# Sample school data: 95 schools with principals, vice-principals, teachers
# ---------------------------------------------------------------------------

FIRST_NAMES_M = [
    "Oluwaseun",
    "Adewale",
    "Chinedu",
    "Ibrahim",
    "Oluwadamilola",
    "Emeka",
    "Tunde",
    "Kolade",
    "Babatunde",
    "Femi",
    "Sunday",
    "Yemi",
    "Kayode",
    "Obinna",
    "Segun",
    "Blessing",
    "Akin",
    "Dare",
    "Nosa",
    "Gbenga",
]

FIRST_NAMES_F = [
    "Aderonke",
    "Folake",
    "Chioma",
    "Amina",
    "Oluwabunmi",
    "Ngozi",
    "Funke",
    "Bukola",
    "Adaeze",
    "Halima",
    "Titilayo",
    "Yetunde",
    "Amara",
    "Kemi",
    "Ifeoma",
    "Blessing",
    "Olayinka",
    "Tolu",
    "Nneka",
    "Grace",
]

LAST_NAMES = [
    "Adeyemi",
    "Ogundimu",
    "Nwosu",
    "Abubakar",
    "Bakare",
    "Eze",
    "Adesanya",
    "Okafor",
    "Lawal",
    "Olumide",
    "Ibrahim",
    "Akande",
    "Chukwu",
    "Bello",
    "Fashola",
    "Onwueme",
    "Tinubu",
    "Obi",
    "Aliyu",
    "Ogunleye",
    "Ajayi",
    "Amadi",
    "Mohammed",
    "Olaniyan",
    "Igwe",
    "Adeleke",
    "Osagie",
    "Uche",
    "Olawale",
    "Akinola",
]

MALE_NAMES = FIRST_NAMES_M
FEMALE_NAMES = FIRST_NAMES_F

# Reference data for Staff/Student profile fields
LAGOS_STATES = ["Lagos", "Ogun", "Oyo", "Ondo", "Osun", "Ekiti", "Kano", "Abuja"]
LAGOS_LGAS = [
    "Agege",
    "Ajeromi-Ifelodun",
    "Alimosho",
    "Amuwo-Odofin",
    "Badagry",
    "Epe",
    "Eti-Osa",
    "Ibeju-Lekki",
    "Ikeja",
    "Ikorodu",
    "Lagos Island",
    "Lagos Mainland",
    "Mushin",
    "Ojo",
    "Oshodi-Isolo",
    "Shomolu",
    "Surulere",
]
BANK_NAMES = [
    "First Bank of Nigeria",
    "Guaranty Trust Bank",
    "United Bank for Africa",
    "Access Bank",
    "Zenith Bank",
    "Stanbic IBTC Bank",
    "First City Monument Bank",
    "Union Bank",
    "Wema Bank",
    "Sterling Bank",
]
STATES_OF_ORIGIN = [
    "Lagos",
    "Ogun",
    "Oyo",
    "Ondo",
    "Osun",
    "Ekiti",
    "Kano",
    "Kaduna",
    "Abia",
    "Anambra",
    "Enugu",
    "Imo",
    "Ebonyi",
    "Delta",
    "Edo",
    "Rivers",
]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
OCCUPATIONS = [
    "Teacher",
    "Engineer",
    "Trader",
    "Civil Servant",
    "Doctor",
    "Lawyer",
    "Banker",
    "Accountant",
    "Nurse",
    "Mechanic",
    "Driver",
    "Farmer",
]


class Command(BaseCommand):
    help = "Seed Education District IV admin users, sample school staff, and students"

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-students",
            action="store_true",
            help="Also create sample student accounts (requires schools to be seeded first)",
        )

    def _upsert_user(self, data, is_staff=False, is_superuser=False):
        """Create or update a user. Only sets password for new users.

        Password changes should go through the API change_password endpoint
        or the reset_password management command -- NOT through re-seeding.
        """
        user, created = User.objects.get_or_create(
            email=data["email"],
            defaults={
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "role": data["role"],
                "phone_number": data.get("phone_number", ""),
                "is_staff": is_staff,
                "is_superuser": is_superuser,
                "is_active": True,
            },
        )
        if created:
            user.set_password(data["password"])
            user.save()
        else:
            changed = False
            for field in ("first_name", "last_name", "role", "phone_number"):
                expected = data.get(field, "")
                if expected and getattr(user, field, "") != expected:
                    setattr(user, field, expected)
                    changed = True
            if user.is_staff != is_staff:
                user.is_staff = is_staff
                changed = True
            if user.is_superuser != is_superuser:
                user.is_superuser = is_superuser
                changed = True
            if not user.is_active:
                user.is_active = True
                changed = True
            if changed:
                user.save()
        return user, created

    def _create_staff_profile(self, user, school, designation, gender, staff_counter):
        """Create a Staff record for a school staff user."""
        from apps.staff.models import Staff

        staff_id = f"STF-{school.code}-{staff_counter:04d}"
        employee_number = f"EDIV-{staff_counter:05d}"

        _, created = Staff.objects.get_or_create(
            user=user,
            defaults={
                "staff_id": staff_id,
                "employee_number": employee_number,
                "school": school,
                "category": "TEACHING",
                "designation": designation,
                "employment_type": random.choice(["PERMANENT", "PERMANENT", "CONTRACT"]),
                "qualification": random.choice(["Bachelors", "Masters", "NCE", "HND"]),
                "date_of_birth": date(random.randint(1970, 1995), random.randint(1, 12), random.randint(1, 28)),
                "gender": gender,
                "marital_status": random.choice(["SINGLE", "MARRIED", "MARRIED", "MARRIED"]),
                "state_of_origin": random.choice(STATES_OF_ORIGIN),
                "lga_of_origin": random.choice(LAGOS_LGAS),
                "residential_address": f"{random.randint(1, 200)} {random.choice(['Street', 'Road', 'Avenue', 'Close'])}, Lagos",
                "emergency_contact_name": f"{random.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {random.choice(LAST_NAMES)}",
                "emergency_contact_phone": f"+23480{random.randint(10000000, 99999999)}",
                "bank_name": random.choice(BANK_NAMES),
                "bank_account_number": f"{random.randint(1000000000, 9999999999)}",
                "bank_account_name": user.get_full_name(),
                "pension_pin": f"PIN{random.randint(100000, 999999)}",
                "tax_id": f"TIN{random.randint(100000, 999999)}",
                "date_joined": date(random.randint(2010, 2024), random.randint(1, 12), random.randint(1, 28)),
                "date_of_first_appointment": date(
                    random.randint(2005, 2020), random.randint(1, 12), random.randint(1, 28)
                ),
                "grade_level": random.choice(["GL08", "GL09", "GL10", "GL12", "GL14", "GL15", "GL16", "GL17"]),
                "step": random.randint(1, 12),
                "salary": round(random.uniform(150000, 650000), 2),
                "is_active": True,
            },
        )
        return created

    def _create_student_profile(self, user, school, gender, student_idx):
        """Create a Student record for a student user."""
        from apps.students.models import Student

        admission_number = f"EDV/{school.code}/{date.today().year}/{student_idx:04d}"
        year_of_birth = random.randint(2008, 2014)

        _, created = Student.objects.get_or_create(
            user=user,
            defaults={
                "admission_number": admission_number,
                "school": school,
                "date_of_birth": date(year_of_birth, random.randint(1, 12), random.randint(1, 28)),
                "gender": gender,
                "blood_group": random.choice(BLOOD_GROUPS),
                "nationality": "Nigerian",
                "state_of_origin": random.choice(STATES_OF_ORIGIN),
                "lga_of_origin": random.choice(LAGOS_LGAS),
                "residential_address": f"{random.randint(1, 200)} {random.choice(['Street', 'Road', 'Avenue', 'Close'])}, Lagos",
                "parent_name": f"{random.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {random.choice(LAST_NAMES)}",
                "parent_phone": f"+23480{random.randint(10000000, 99999999)}",
                "parent_email": "",
                "parent_occupation": random.choice(OCCUPATIONS),
                "emergency_contact_name": f"{random.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {random.choice(LAST_NAMES)}",
                "emergency_contact_phone": f"+23480{random.randint(10000000, 99999999)}",
                "admission_date": date(date.today().year, random.choice([9, 1]), random.randint(1, 15)),
                "status": "ACTIVE",
                "is_boarding": random.choice([True, False, False]),
            },
        )
        return created

    def handle(self, *args, **options):
        random.seed(42)

        # --- Admin / Head Office Users ---
        self.stdout.write(self.style.NOTICE("\n--- Seeding admin users ---"))
        admin_created = 0
        admin_updated = 0
        for data in ADMIN_USERS:
            try:
                user, created = self._upsert_user(
                    data,
                    is_staff=data.get("is_staff", False),
                    is_superuser=data.get("is_superuser", False),
                )
                if created:
                    admin_created += 1
                    self.stdout.write(f"  + Admin: {user.email} ({user.role})")
                else:
                    admin_updated += 1
                    self.stdout.write(f"  ~ Updated: {user.email} ({user.role})")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ! Failed: {data["email"]} - {e}'))

        self.stdout.write(self.style.SUCCESS(f"  Admin users: {admin_created} created, {admin_updated} updated"))

        # --- Department Heads ---
        self.stdout.write(self.style.NOTICE("\n--- Seeding department heads ---"))
        from apps.departments.models import Department

        dept_head_created = 0
        dept_head_updated = 0
        for data in DEPARTMENT_HEADS:
            try:
                user, created = self._upsert_user(data, is_staff=True)
                if created:
                    dept_head_created += 1
                else:
                    dept_head_updated += 1

                # Link head to department
                dept_code = data.get("department_code")
                if dept_code:
                    try:
                        dept = Department.objects.get(code=dept_code)
                        if dept.head_id != user.id:
                            dept.head = user
                            dept.save(update_fields=["head"])
                    except Department.DoesNotExist:
                        pass
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ! Failed: {data["email"]} - {e}'))

        self.stdout.write(
            self.style.SUCCESS(f"  Department heads: {dept_head_created} created, {dept_head_updated} updated")
        )

        # --- Major Unit Heads ---
        self.stdout.write(self.style.NOTICE("\n--- Seeding major unit heads ---"))
        from apps.departments.models import Unit

        unit_head_created = 0
        unit_head_updated = 0
        for data in UNIT_HEADS:
            try:
                user, created = self._upsert_user(data, is_staff=True)
                if created:
                    unit_head_created += 1
                else:
                    unit_head_updated += 1

                # Link head to unit
                unit_code = data.get("unit_code")
                if unit_code:
                    try:
                        unit = Unit.objects.get(code=unit_code)
                        if unit.head_id != user.id:
                            unit.head = user
                            unit.save(update_fields=["head"])
                    except Unit.DoesNotExist:
                        pass
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ! Failed: {data["email"]} - {e}'))

        self.stdout.write(self.style.SUCCESS(f"  Unit heads: {unit_head_created} created, {unit_head_updated} updated"))

        # --- Sample School Staff (Principals, VPs, Teachers) + Staff profiles ---
        self.stdout.write(self.style.NOTICE("\n--- Seeding school staff ---"))
        user_created = 0
        user_updated = 0
        profile_created = 0

        from apps.schools.models import School

        schools = list(School.objects.all())
        if not schools:
            self.stdout.write(
                self.style.WARNING("  No schools found. Run seed_schools command first. Skipping staff seeding.")
            )
            return

        staff_counter = 0
        teacher_idx = 0
        for school in schools:
            # Create Principal + Staff profile
            is_male = random.choice([True, False])
            first_name = random.choice(MALE_NAMES if is_male else FEMALE_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = f"principal_{school.code.lower()}@ediv.gov.ng"
            gender_p = "M" if is_male else "F"

            try:
                user, created = self._upsert_user(
                    {
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": "PRI",
                        "phone_number": f"+234802{random.randint(1000000, 9999999):07d}",
                        "password": SCHOOL_STAFF_PASSWORD,
                    }
                )
                if created:
                    user_created += 1
                else:
                    user_updated += 1
                if school.principal_id != user.id:
                    school.principal = user
                    school.save(update_fields=["principal"])

                # Create Staff record for Principal
                staff_counter += 1
                if self._create_staff_profile(user, school, "PRINCIPAL", gender_p, staff_counter):
                    profile_created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ! Principal failed for {school.code}: {e}"))

            # Create Vice Principal + Staff profile
            is_male2 = not is_male
            first_name2 = random.choice(MALE_NAMES if is_male2 else FEMALE_NAMES)
            last_name2 = random.choice(LAST_NAMES)
            email2 = f"vp_{school.code.lower()}@ediv.gov.ng"
            gender_v = "M" if is_male2 else "F"

            try:
                user2, created2 = self._upsert_user(
                    {
                        "email": email2,
                        "first_name": first_name2,
                        "last_name": last_name2,
                        "role": "VP",
                        "phone_number": f"+234803{random.randint(1000000, 9999999):07d}",
                        "password": SCHOOL_STAFF_PASSWORD,
                    }
                )
                if created2:
                    user_created += 1
                else:
                    user_updated += 1
                if school.vice_principal_id != user2.id:
                    school.vice_principal = user2
                    school.save(update_fields=["vice_principal"])

                # Create Staff record for VP
                staff_counter += 1
                if self._create_staff_profile(user2, school, "VICE_PRINCIPAL", gender_v, staff_counter):
                    profile_created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ! VP failed for {school.code}: {e}"))

            # Create 3-5 teachers per school + Staff profiles
            num_teachers = random.randint(3, 5)
            for i in range(num_teachers):
                teacher_idx += 1
                is_male_t = random.choice([True, False])
                first_t = random.choice(MALE_NAMES if is_male_t else FEMALE_NAMES)
                last_t = random.choice(LAST_NAMES)
                email_t = f"teacher_{teacher_idx:04d}@ediv.gov.ng"
                gender_t = "M" if is_male_t else "F"

                try:
                    user_t, created_t = self._upsert_user(
                        {
                            "email": email_t,
                            "first_name": first_t,
                            "last_name": last_t,
                            "role": "TCH",
                            "phone_number": f"+234804{random.randint(1000000, 9999999):07d}",
                            "password": TEACHER_PASSWORD,
                        }
                    )
                    if created_t:
                        user_created += 1
                    else:
                        user_updated += 1

                    # Create Staff record for Teacher
                    staff_counter += 1
                    if self._create_staff_profile(user_t, school, "TEACHER", gender_t, staff_counter):
                        profile_created += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ! Teacher {email_t} failed: {e}"))

        self.stdout.write(self.style.SUCCESS(f"  School staff users: {user_created} created, {user_updated} updated"))
        self.stdout.write(self.style.SUCCESS(f"  Staff profiles: {profile_created} created"))

        # --- Sample Students + Student profiles ---
        if options["with_students"]:
            self.stdout.write(self.style.NOTICE("\n--- Seeding sample students ---"))
            student_created = 0
            student_skipped = 0
            student_profile_created = 0
            student_idx = 0

            for school in schools:
                # 2-4 students per school
                num_students = random.randint(2, 4)
                for i in range(num_students):
                    student_idx += 1
                    is_male_s = random.choice([True, False])
                    first_s = random.choice(MALE_NAMES if is_male_s else FEMALE_NAMES)
                    last_s = random.choice(LAST_NAMES)
                    email_s = f"student_{student_idx:04d}@student.ediv.gov.ng"
                    gender_s = "M" if is_male_s else "F"

                    user_s, created_s = User.objects.get_or_create(
                        email=email_s,
                        defaults={
                            "first_name": first_s,
                            "last_name": last_s,
                            "role": "STD",
                            "phone_number": "",
                        },
                    )
                    if created_s:
                        user_s.set_password(STUDENT_PASSWORD)
                        user_s.save()
                        student_created += 1

                        # Create Student profile
                        if self._create_student_profile(user_s, school, gender_s, student_idx):
                            student_profile_created += 1
                    else:
                        student_skipped += 1

            self.stdout.write(self.style.SUCCESS(f"  Students: {student_created} created, {student_skipped} skipped"))
            self.stdout.write(self.style.SUCCESS(f"  Student profiles: {student_profile_created} created"))

        self.stdout.write(self.style.SUCCESS("\nAll seeding complete!"))
