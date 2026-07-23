import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from apps.schools.models import School


# School data: realistic Lagos school names across Apapa, Mainland, Surulere

APAPA_SCHOOLS = [
    ('Adeola Primary/Secondary School', 'APU001', 'SENIOR', 'APAPA'),
    ('Apapa GRA Secondary School', 'APU002', 'SENIOR', 'APAPA'),
    ('Apapa Junior Secondary School', 'APU003', 'JUNIOR', 'APAPA'),
    ('Apapa Senior Secondary School', 'APU004', 'SENIOR', 'APAPA'),
    ('Apapa Senior Junior Secondary School', 'APU005', 'JUNIOR', 'APAPA'),
    ('Apapa-Ajeromi Ifelodun Junior Secondary School', 'APU006', 'JUNIOR', 'APAPA'),
    ('Apapa-Ajeromi Ifelodun Senior Secondary School', 'APU007', 'SENIOR', 'APAPA'),
    ('Babatunde Oluwatoki Memorial Secondary School', 'APU008', 'SENIOR', 'APAPA'),
    ('Badia Junior Secondary School', 'APU009', 'JUNIOR', 'APAPA'),
    ('Badia Senior Secondary School', 'APU010', 'SENIOR', 'APAPA'),
    ('Caroline Memorial Junior Secondary School', 'APU011', 'JUNIOR', 'APAPA'),
    ('Caroline Memorial Senior Secondary School', 'APU012', 'SENIOR', 'APAPA'),
    ('E.A Adeleye Memorial Secondary School', 'APU013', 'SENIOR', 'APAPA'),
    ('Eleko Junior Secondary School', 'APU014', 'JUNIOR', 'APAPA'),
    ('Eleko Senior Secondary School', 'APU015', 'SENIOR', 'APAPA'),
    ('Fatima Memorial Junior Secondary School', 'APU016', 'JUNIOR', 'APAPA'),
    ('Fatima Memorial Senior Secondary School', 'APU017', 'SENIOR', 'APAPA'),
    ('Gaskiya Junior Secondary School', 'APU018', 'JUNIOR', 'APAPA'),
    ('Gaskiya Senior Secondary School', 'APU019', 'SENIOR', 'APAPA'),
    ('Ibafon Junior Secondary School', 'APU020', 'JUNIOR', 'APAPA'),
    ('Ibafon Senior Secondary School', 'APU021', 'SENIOR', 'APAPA'),
    ('Kirikiri Junior Secondary School', 'APU022', 'JUNIOR', 'APAPA'),
    ('Kirikiri Senior Secondary School', 'APU023', 'SENIOR', 'APAPA'),
    ('Mile 2 Junior Secondary School', 'APU024', 'JUNIOR', 'APAPA'),
    ('Mile 2 Senior Secondary School', 'APU025', 'SENIOR', 'APAPA'),
    ('Ojo Road Junior Secondary School', 'APU026', 'JUNIOR', 'APAPA'),
    ('Ojo Road Senior Secondary School', 'APU027', 'SENIOR', 'APAPA'),
    ('Sango Junior Secondary School', 'APU028', 'JUNIOR', 'APAPA'),
    ('Sango Senior Secondary School', 'APU029', 'SENIOR', 'APAPA'),
    ('Tincan Island Junior Secondary School', 'APU030', 'JUNIOR', 'APAPA'),
]

MAINLAND_SCHOOLS = [
    ('Ajeromi-Ifelodun Junior Secondary School', 'MLA001', 'JUNIOR', 'MAINLAND'),
    ('Ajeromi-Ifelodun Senior Secondary School', 'MLA002', 'SENIOR', 'MAINLAND'),
    ('Akoka Junior Secondary School', 'MLA003', 'JUNIOR', 'MAINLAND'),
    ('Akoka Senior Secondary School', 'MLA004', 'SENIOR', 'MAINLAND'),
    ('Bariga Junior Secondary School', 'MLA005', 'JUNIOR', 'MAINLAND'),
    ('Bariga Senior Secondary School', 'MLA006', 'SENIOR', 'MAINLAND'),
    ('Herbert Macaulay Junior Secondary School', 'MLA007', 'JUNIOR', 'MAINLAND'),
    ('Herbert Macaulay Senior Secondary School', 'MLA008', 'SENIOR', 'MAINLAND'),
    ('Igbobi Junior Secondary School', 'MLA009', 'JUNIOR', 'MAINLAND'),
    ('Igbobi Senior Secondary School', 'MLA010', 'SENIOR', 'MAINLAND'),
    ('Jibowu Junior Secondary School', 'MLA011', 'JUNIOR', 'MAINLAND'),
    ('Jibowu Senior Secondary School', 'MLA012', 'SENIOR', 'MAINLAND'),
    ('Lawanson Junior Secondary School', 'MLA013', 'JUNIOR', 'MAINLAND'),
    ('Lawanson Senior Secondary School', 'MLA014', 'SENIOR', 'MAINLAND'),
    ('Lagos Island Junior Secondary School', 'MLA015', 'JUNIOR', 'MAINLAND'),
    ('Lagos Island Senior Secondary School', 'MLA016', 'SENIOR', 'MAINLAND'),
    ('Maroko Junior Secondary School', 'MLA017', 'JUNIOR', 'MAINLAND'),
    ('Maroko Senior Secondary School', 'MLA018', 'SENIOR', 'MAINLAND'),
    ('Oyingbo Junior Secondary School', 'MLA019', 'JUNIOR', 'MAINLAND'),
    ('Oyingbo Senior Secondary School', 'MLA020', 'SENIOR', 'MAINLAND'),
    ('Sabo Junior Secondary School', 'MLA021', 'JUNIOR', 'MAINLAND'),
    ('Sabo Senior Secondary School', 'MLA022', 'SENIOR', 'MAINLAND'),
    ('Ebute Metta Junior Secondary School', 'MLA023', 'JUNIOR', 'MAINLAND'),
    ('Ebute Metta Senior Secondary School', 'MLA024', 'SENIOR', 'MAINLAND'),
    ('Papa Ajao Junior Secondary School', 'MLA025', 'JUNIOR', 'MAINLAND'),
    ('Papa Ajao Senior Secondary School', 'MLA026', 'SENIOR', 'MAINLAND'),
    ('St. Agnes Junior Secondary School', 'MLA027', 'JUNIOR', 'MAINLAND'),
    ('St. Agnes Senior Secondary School', 'MLA028', 'SENIOR', 'MAINLAND'),
    ('Yaba Junior Secondary School', 'MLA029', 'JUNIOR', 'MAINLAND'),
    ('Yaba Senior Secondary School', 'MLA030', 'SENIOR', 'MAINLAND'),
    ('Onike Junior Secondary School', 'MLA031', 'JUNIOR', 'MAINLAND'),
    ('Onike Senior Secondary School', 'MLA032', 'SENIOR', 'MAINLAND'),
    ('Tejuosho Junior Secondary School', 'MLA033', 'JUNIOR', 'MAINLAND'),
    ('Tejuosho Senior Secondary School', 'MLA034', 'SENIOR', 'MAINLAND'),
    ('Ojuelegba Junior Secondary School', 'MLA035', 'JUNIOR', 'MAINLAND'),
]

SURULERE_SCHOOLS = [
    ('Aguda Junior Secondary School', 'SUR001', 'JUNIOR', 'SURULERE'),
    ('Aguda Senior Secondary School', 'SUR002', 'SENIOR', 'SURULERE'),
    ('Bode Thomas Junior Secondary School', 'SUR003', 'JUNIOR', 'SURULERE'),
    ('Bode Thomas Senior Secondary School', 'SUR004', 'SENIOR', 'SURULERE'),
    ('Idi-Araba Junior Secondary School', 'SUR005', 'JUNIOR', 'SURULERE'),
    ('Idi-Araba Senior Secondary School', 'SUR006', 'SENIOR', 'SURULERE'),
    ('Ijesha Junior Secondary School', 'SUR007', 'JUNIOR', 'SURULERE'),
    ('Ijesha Senior Secondary School', 'SUR008', 'SENIOR', 'SURULERE'),
    ('Itire Junior Secondary School', 'SUR009', 'JUNIOR', 'SURULERE'),
    ('Itire Senior Secondary School', 'SUR010', 'SENIOR', 'SURULERE'),
    ('Lawanson Junior Secondary School', 'SUR011', 'JUNIOR', 'SURULERE'),
    ('Lawanson Senior Secondary School', 'SUR012', 'SENIOR', 'SURULERE'),
    ('Ogunlana Drive Junior Secondary School', 'SUR013', 'JUNIOR', 'SURULERE'),
    ('Ogunlana Drive Senior Secondary School', 'SUR014', 'SENIOR', 'SURULERE'),
    ('Ojuelegba Junior Secondary School', 'SUR015', 'JUNIOR', 'SURULERE'),
    ('Ojuelegba Senior Secondary School', 'SUR016', 'SENIOR', 'SURULERE'),
    ('Orile Junior Secondary School', 'SUR017', 'JUNIOR', 'SURULERE'),
    ('Orile Senior Secondary School', 'SUR018', 'SENIOR', 'SURULERE'),
    ('Shomolu Junior Secondary School', 'SUR019', 'JUNIOR', 'SURULERE'),
    ('Shomolu Senior Secondary School', 'SUR020', 'SENIOR', 'SURULERE'),
    ('Akerele Junior Secondary School', 'SUR021', 'JUNIOR', 'SURULERE'),
    ('Akerele Senior Secondary School', 'SUR022', 'SENIOR', 'SURULERE'),
    ('Adeniran Ogunsanya Junior Secondary School', 'SUR023', 'JUNIOR', 'SURULERE'),
    ('Adeniran Ogunsanya Senior Secondary School', 'SUR024', 'SENIOR', 'SURULERE'),
    ('Masha Junior Secondary School', 'SUR025', 'JUNIOR', 'SURULERE'),
    ('Masha Senior Secondary School', 'SUR026', 'SENIOR', 'SURULERE'),
    ('Igando Junior Secondary School', 'SUR027', 'JUNIOR', 'SURULERE'),
    ('Igando Senior Secondary School', 'SUR028', 'SENIOR', 'SURULERE'),
    ('Coker Junior Secondary School', 'SUR029', 'JUNIOR', 'SURULERE'),
    ('Coker Senior Secondary School', 'SUR030', 'SENIOR', 'SURULERE'),
]

ALL_SCHOOLS = APAPA_SCHOOLS + MAINLAND_SCHOOLS + SURULERE_SCHOOLS


ADDRESSES = {
    'APAPA': [
        '5 Apapa Road, Apapa, Lagos',
        '12 Creek Road, Apapa, Lagos',
        '8 Wharf Road, Apapa, Lagos',
        '15 Beecroft Street, Apapa, Lagos',
        '20 Apapa-Oshodi Expressway, Apapa, Lagos',
    ],
    'MAINLAND': [
        '10 Yaba Road, Yaba, Lagos',
        '25 Herbert Macaulay Way, Yaba, Lagos',
        '14 Murtala Muhammed Way, Yaba, Lagos',
        '7 Anthony Village Road, Anthony, Lagos',
        '18 Jibowu Street, Yaba, Lagos',
    ],
    'SURULERE': [
        '3 Bode Thomas Avenue, Surulere, Lagos',
        '12 Adeniran Ogunsanya Street, Surulere, Lagos',
        '8 Ogunlana Drive, Surulere, Lagos',
        '15 Ojuelegba Road, Surulere, Lagos',
        '22 Aguda Street, Surulere, Lagos',
    ],
}


class Command(BaseCommand):
    help = 'Seed Education District IV schools across Apapa, Mainland, Surulere LGAs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding schools...'))

        created_count = 0
        skipped_count = 0
        random.seed(42)

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
