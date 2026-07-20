import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from apps.schools.models import School


# ---------------------------------------------------------------------------
# School data: realistic Lagos school names across Apapa, Mainland, Surulere
# ---------------------------------------------------------------------------

APAPA_SCHOOLS = [
    ('Adeola Primary/Secondary School', 'APU001', 'SENIOR', 'Apapa'),
    ('Apapa GRA Secondary School', 'APU002', 'SENIOR', 'Apapa'),
    ('Apapa Junior Secondary School', 'APU003', 'JUNIOR', 'Apapa'),
    ('Apapa Senior Secondary School', 'APU004', 'SENIOR', 'Apapa'),
    ('Apapa Senior Junior Secondary School', 'APU005', 'JUNIOR', 'Apapa'),
    ('Apapa-Ajeromi Ifelodun Junior Secondary School', 'APU006', 'JUNIOR', 'Apapa'),
    ('Apapa-Ajeromi Ifelodun Senior Secondary School', 'APU007', 'SENIOR', 'Apapa'),
    ('Babatunde Oluwatoki Memorial Secondary School', 'APU008', 'SENIOR', 'Apapa'),
    ('Badia Junior Secondary School', 'APU009', 'JUNIOR', 'Apapa'),
    ('Badia Senior Secondary School', 'APU010', 'SENIOR', 'Apapa'),
    ('Caroline Memorial Junior Secondary School', 'APU011', 'JUNIOR', 'Apapa'),
    ('Caroline Memorial Senior Secondary School', 'APU012', 'SENIOR', 'Apapa'),
    ('E.A Adeleye Memorial Secondary School', 'APU013', 'SENIOR', 'Apapa'),
    ('Eleko Junior Secondary School', 'APU014', 'JUNIOR', 'Apapa'),
    ('Eleko Senior Secondary School', 'APU015', 'SENIOR', 'Apapa'),
    ('Fatima Memorial Junior Secondary School', 'APU016', 'JUNIOR', 'Apapa'),
    ('Fatima Memorial Senior Secondary School', 'APU017', 'SENIOR', 'Apapa'),
    ('Gaskiya Junior Secondary School', 'APU018', 'JUNIOR', 'Apapa'),
    ('Gaskiya Senior Secondary School', 'APU019', 'SENIOR', 'Apapa'),
    ('Ibafon Junior Secondary School', 'APU020', 'JUNIOR', 'Apapa'),
    ('Ibafon Senior Secondary School', 'APU021', 'SENIOR', 'Apapa'),
    ('Kirikiri Junior Secondary School', 'APU022', 'JUNIOR', 'Apapa'),
    ('Kirikiri Senior Secondary School', 'APU023', 'SENIOR', 'Apapa'),
    ('Mile 2 Junior Secondary School', 'APU024', 'JUNIOR', 'Apapa'),
    ('Mile 2 Senior Secondary School', 'APU025', 'SENIOR', 'Apapa'),
    ('Ojo Road Junior Secondary School', 'APU026', 'JUNIOR', 'Apapa'),
    ('Ojo Road Senior Secondary School', 'APU027', 'SENIOR', 'Apapa'),
    ('Sango Junior Secondary School', 'APU028', 'JUNIOR', 'Apapa'),
    ('Sango Senior Secondary School', 'APU029', 'SENIOR', 'Apapa'),
    ('Tincan Junior Secondary School', 'APU030', 'JUNIOR', 'Apapa'),
]

MAINLAND_SCHOOLS = [
    ('Abigail Secondary School', 'MLA001', 'SENIOR', 'Mainland'),
    ('Ahmadiyya Junior Secondary School', 'MLA002', 'JUNIOR', 'Mainland'),
    ('Ahmadiyya Senior Secondary School', 'MLA003', 'SENIOR', 'Mainland'),
    ('Akoka Junior Secondary School', 'MLA004', 'JUNIOR', 'Mainland'),
    ('Akoka Senior Secondary School', 'MLA005', 'SENIOR', 'Mainland'),
    ('Anthony Village Junior Secondary School', 'MLA006', 'JUNIOR', 'Mainland'),
    ('Anthony Village Senior Secondary School', 'MLA007', 'SENIOR', 'Mainland'),
    ('Bariga Junior Secondary School', 'MLA008', 'JUNIOR', 'Mainland'),
    ('Bariga Senior Secondary School', 'MLA009', 'SENIOR', 'Mainland'),
    ('Bode Thomas Junior Secondary School', 'MLA010', 'JUNIOR', 'Mainland'),
    ('Bode Thomas Senior Secondary School', 'MLA011', 'SENIOR', 'Mainland'),
    ('Balogun Memorial Junior Secondary School', 'MLA012', 'JUNIOR', 'Mainland'),
    ('Balogun Memorial Senior Secondary School', 'MLA013', 'SENIOR', 'Mainland'),
    ('Edward Musingderi Junior Secondary School', 'MLA014', 'JUNIOR', 'Mainland'),
    ('Edward Musingderi Senior Secondary School', 'MLA015', 'SENIOR', 'Mainland'),
    ('Gbaja Junior Secondary School', 'MLA016', 'JUNIOR', 'Mainland'),
    ('Gbaja Senior Secondary School', 'MLA017', 'SENIOR', 'Mainland'),
    ('Herbert Macaulay Junior Secondary School', 'MLA018', 'JUNIOR', 'Mainland'),
    ('Herbert Macaulay Senior Secondary School', 'MLA019', 'SENIOR', 'Mainland'),
    ('Ijaye Junior Secondary School', 'MLA020', 'JUNIOR', 'Mainland'),
    ('Ijaye Senior Secondary School', 'MLA021', 'SENIOR', 'Mainland'),
    ('Itire Junior Secondary School', 'MLA022', 'JUNIOR', 'Mainland'),
    ('Itire Senior Secondary School', 'MLA023', 'SENIOR', 'Mainland'),
    ('Jibowu Junior Secondary School', 'MLA024', 'JUNIOR', 'Mainland'),
    ('Jibowu Senior Secondary School', 'MLA025', 'SENIOR', 'Mainland'),
    ('Ketu Junior Secondary School', 'MLA026', 'JUNIOR', 'Mainland'),
    ('Ketu Senior Secondary School', 'MLA027', 'SENIOR', 'Mainland'),
    ('Lawanson Junior Secondary School', 'MLA028', 'JUNIOR', 'Mainland'),
    ('Lawanson Senior Secondary School', 'MLA029', 'SENIOR', 'Mainland'),
    ('Maryland Junior Secondary School', 'MLA030', 'JUNIOR', 'Mainland'),
    ('Maryland Senior Secondary School', 'MLA031', 'SENIOR', 'Mainland'),
    ('Oworonsoki Junior Secondary School', 'MLA032', 'JUNIOR', 'Mainland'),
    ('Oworonsoki Senior Secondary School', 'MLA033', 'SENIOR', 'Mainland'),
    ('Pedro Junior Secondary School', 'MLA034', 'JUNIOR', 'Mainland'),
    ('Pedro Senior Secondary School', 'MLA035', 'SENIOR', 'Mainland'),
]

SURULERE_SCHOOLS = [
    ('Adeniran Ogunsanya Junior Secondary School', 'SUR001', 'JUNIOR', 'Surulere'),
    ('Adeniran Ogunsanya Senior Secondary School', 'SUR002', 'SENIOR', 'Surulere'),
    ('Akinwunmi Junior Secondary School', 'SUR003', 'JUNIOR', 'Surulere'),
    ('Akinwunmi Senior Secondary School', 'SUR004', 'SENIOR', 'Surulere'),
    ('Babs Fafunwa Junior Secondary School', 'SUR005', 'JUNIOR', 'Surulere'),
    ('Babs Fafunwa Senior Secondary School', 'SUR006', 'SENIOR', 'Surulere'),
    ('Ijesha Junior Secondary School', 'SUR007', 'JUNIOR', 'Surulere'),
    ('Ijesha Senior Secondary School', 'SUR008', 'SENIOR', 'Surulere'),
    ('Itire-Ikate Junior Secondary School', 'SUR009', 'JUNIOR', 'Surulere'),
    ('Itire-Ikate Senior Secondary School', 'SUR010', 'SENIOR', 'Surulere'),
    ('Jibiti Memorial Junior Secondary School', 'SUR011', 'JUNIOR', 'Surulere'),
    ('Jibiti Memorial Senior Secondary School', 'SUR012', 'SENIOR', 'Surulere'),
    ('Lawanson Junior Secondary School', 'SUR013', 'JUNIOR', 'Surulere'),
    ('Lawanson Senior Secondary School', 'SUR014', 'SENIOR', 'Surulere'),
    ('Maryland Junior Secondary School', 'SUR015', 'JUNIOR', 'Surulere'),
    ('Maryland Senior Secondary School', 'SUR016', 'SENIOR', 'Surulere'),
    ('Mosafejo Junior Secondary School', 'SUR017', 'JUNIOR', 'Surulere'),
    ('Mosafejo Senior Secondary School', 'SUR018', 'SENIOR', 'Surulere'),
    ('Onikan Junior Secondary School', 'SUR019', 'JUNIOR', 'Surulere'),
    ('Onikan Senior Secondary School', 'SUR020', 'SENIOR', 'Surulere'),
    ('Oregun Junior Secondary School', 'SUR021', 'JUNIOR', 'Surulere'),
    ('Oregun Senior Secondary School', 'SUR022', 'SENIOR', 'Surulere'),
    ('Shomolu Junior Secondary School', 'SUR023', 'JUNIOR', 'Surulere'),
    ('Shomolu Senior Secondary School', 'SUR024', 'SENIOR', 'Surulere'),
    ('St. Agnes Junior Secondary School', 'SUR025', 'JUNIOR', 'Surulere'),
    ('St. Agnes Senior Secondary School', 'SUR026', 'SENIOR', 'Surulere'),
    ('Surulere Junior Secondary School', 'SUR027', 'JUNIOR', 'Surulere'),
    ('Surulere Senior Secondary School', 'SUR028', 'SENIOR', 'Surulere'),
    ('Yaba Junior Secondary School', 'SUR029', 'JUNIOR', 'Surulere'),
    ('Yaba Senior Secondary School', 'SUR030', 'SENIOR', 'Surulere'),
]

ALL_SCHOOLS = APAPA_SCHOOLS + MAINLAND_SCHOOLS + SURULERE_SCHOOLS

ADDRESSES = {
    'APAPA': [
        'No. 1 Apapa Road, Apapa, Lagos',
        '5 Creek Road, Apapa, Lagos',
        '12 Apapa-Oshodi Expressway, Apapa, Lagos',
        '3 Wharf Road, Apapa, Lagos',
        '8 Marine Road, Apapa, Lagos',
        '21 Tincan Island Road, Apapa, Lagos',
        '7 Sapele Street, Apapa, Lagos',
        '14 Port Road, Apapa, Lagos',
    ],
    'MAINLAND': [
        '15 Herbert Macaulay Way, Yaba, Lagos',
        '23 Murtala Muhammed Way, Yaba, Lagos',
        '8 Akoka Road, Bariga, Lagos',
        '11 Bode Thomas Street, Surulere, Lagos',
        '4 Ikorodu Road, Bariga, Lagos',
        '9 Anthony Village Road, Anthony, Lagos',
        '18 Jibowu Street, Yaba, Lagos',
        '6 Ojuelegba Road, Surulere, Lagos',
    ],
    'SURULERE': [
        '10 Adeniran Ogunsanya Street, Surulere, Lagos',
        '17 Bode Thomas Avenue, Surulere, Lagos',
        '3 Lawanson Road, Surulere, Lagos',
        '22 Aguda Street, Surulere, Lagos',
        '8 Ogunlana Drive, Surulere, Lagos',
        '14 Ojuelegba Crescent, Surulere, Lagos',
        '5 Shipeolu Street, Surulere, Lagos',
        '19 Akerele Extension, Surulere, Lagos',
    ],
}


class Command(BaseCommand):
    help = 'Seed Education District IV schools across Apapa, Mainland, and Surulere LGAs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding schools...'))

        created_count = 0
        skipped_count = 0
        random.seed(42)  # Reproducible results

        for name, code, school_type, lga in ALL_SCHOOLS:
            address = random.choice(ADDRESSES[lga])
            est_year = random.randint(1975, 2015)
            capacity = random.choice([600, 800, 1000, 1200, 1500, 1800, 2000])
            enrollment = random.randint(int(capacity * 0.4), int(capacity * 0.95))
            classrooms = random.randint(12, 30)
            staff_count = random.randint(15, 45)

            school, created = School.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'school_type': school_type,
                    'lga': lga,
                    'address': address,
                    'established_date': date(est_year, random.randint(1, 12), random.randint(1, 28)),
                    'student_capacity': capacity,
                    'current_enrollment': enrollment,
                    'number_of_classrooms': classrooms,
                    'number_of_staff': staff_count,
                    'has_science_lab': random.choice([True, False]),
                    'has_computer_lab': random.choice([True, False]),
                    'has_library': random.choice([True, True, False]),
                    'has_sports_field': random.choice([True, True, True, False]),
                },
            )
            if created:
                created_count += 1
                self.stdout.write(f'  + [{code}] {name} ({school_type} - {lga})')
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {created_count} schools created, {skipped_count} already existed.'
        ))
