from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='attachment',
            field=models.FileField(
                blank=True,
                help_text='Upload file (JPEG, PDF, Excel, Word, etc.)',
                upload_to='registry/documents/',
            ),
        ),
    ]
