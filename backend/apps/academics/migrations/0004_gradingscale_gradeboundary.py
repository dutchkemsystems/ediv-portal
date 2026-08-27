from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0001_initial'),
        ('academics', '0003_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradingScale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('academic_year', models.CharField(max_length=9)),
                ('term', models.CharField(
                    choices=[
                        ('FIRST', 'First Term'),
                        ('SECOND', 'Second Term'),
                        ('THIRD', 'Third Term'),
                        ('ALL', 'All Terms'),
                    ],
                    default='ALL',
                    max_length=20,
                )),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='grading_scales',
                    to='schools.school',
                )),
            ],
            options={
                'ordering': ['school', '-academic_year'],
                'unique_together': {('school', 'name', 'academic_year')},
            },
        ),
        migrations.CreateModel(
            name='GradeBoundary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.CharField(max_length=5)),
                ('min_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('max_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('remark', models.CharField(blank=True, max_length=50)),
                ('grading_scale', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='boundaries',
                    to='academics.gradingscale',
                )),
            ],
            options={
                'ordering': ['grading_scale', '-min_percentage'],
                'unique_together': {('grading_scale', 'grade')},
            },
        ),
    ]
