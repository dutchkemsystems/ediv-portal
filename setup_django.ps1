# setup_django.ps1
Write-Host "🚀 Setting up Django Server for Education District IV Portal..."

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install Django==4.2.7 djangorestframework==3.14.0 django-cors-headers==4.3.1 dj-database-url==2.1.0 psycopg2-binary==2.9.9 gunicorn==21.2.0 whitenoise==6.6.0 python-dotenv==1.0.0

# Freeze requirements
pip freeze > requirements.txt

# Create project and app
django-admin startproject ediv_portal .
python manage.py startapp core

# Migrate and create superuser
python manage.py migrate
python manage.py createsuperuser

Write-Host "✅ Django server setup complete!"
Write-Host "Run 'python manage.py runserver' to start."