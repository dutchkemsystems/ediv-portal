# Education District IV Portal

## Overview

Comprehensive digital ecosystem for Education District IV — serving 80,000+ students, 5,000+ staff across 95 schools in Apapa, Mainland, and Surulere Local Government Areas.

## Mission

To provide a seamless, efficient, and transparent digital ecosystem that empowers educators, administrators, students, and parents through innovative technology, fostering excellence in education delivery and administrative efficiency.

## Features

### Core Modules
- **School Management** - 95 schools across 3 LGAs
- **Staff Management** - 5,000+ staff with HR, payroll, and performance tracking
- **Student Management** - 80,000+ students with enrollment and academic tracking
- **Academic Management** - Classes, subjects, exams, and report cards
- **Finance Module** - Fee management, payments, and budgeting
- **E-Registry** - Digital file creation, tracking, and circulation
- **Workflow Automation** - Task assignment, approval, and escalation
- **Communication** - Internal messaging, notifications, and circulars

### Additional Features
- **Data Import/Export** - Excel, PDF, Word, CSV, JPEG support
- **Real-time Tracking** - File movement and task status
- **Role-based Access** - 22+ user roles with permissions
- **Mobile Friendly** - Responsive design for all devices
- **PWA Support** - Offline capability for attendance
- **Multi-language** - French language support

## Tech Stack

### Backend
- Django 4.2+
- Django REST Framework 3.14+
- PostgreSQL 16+
- Redis 7+
- Elasticsearch 8+
- Celery 5.3+
- RabbitMQ 3.12+

### Frontend
- React 18+
- Redux Toolkit
- Material-UI 5
- Vite

### DevOps
- Docker & Docker Compose
- Nginx
- GitHub Actions CI/CD
- Prometheus & Grafana

## Quick Start

### Prerequisites
- Docker 24+
- Docker Compose 2.20+

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/education-district-iv-portal.git
cd education-district-iv-portal

# Copy environment file
cp .env.example .env

# Start development server
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
```

### Default Credentials

| Role | Email | Password |
|------|-------|----------|
| System Admin | admin@ediv.gov.ng | Admin@12345678 |
| Tutor General | tg@ediv.gov.ng | TutorGen@12345 |
| HR Head | hr@ediv.gov.ng | DeptHead@12345 |
| Finance Director | finance@ediv.gov.ng | DeptHead@12345 |

## Development

### Run Tests
```bash
docker-compose exec backend python manage.py test
```

### Run Migrations
```bash
docker-compose exec backend python manage.py migrate
```

### Seed Data
```bash
docker-compose exec backend python manage.py seed_departments
docker-compose exec backend python manage.py seed_users
```

### Access Django Shell
```bash
docker-compose exec backend python manage.py shell
```

## Project Structure

```
education-district-iv/
├── backend/                 # Django backend
│   ├── apps/               # Django apps
│   │   ├── users/          # User management
│   │   ├── schools/        # School management
│   │   ├── staff/          # Staff management
│   │   ├── students/       # Student management
│   │   ├── academics/      # Academic management
│   │   ├── attendance/     # Attendance tracking
│   │   ├── finance/        # Finance management
│   │   ├── files/          # E-Registry
│   │   ├── workflows/      # Workflow automation
│   │   └── ...             # Other modules
│   ├── config/             # Django configuration
│   └── requirements/       # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── store/          # Redux store
│   │   └── api/            # API client
│   └── package.json
├── docker/                 # Docker configuration
├── scripts/                # Deployment scripts
└── docs/                   # Documentation
```

## API Documentation

See [API Documentation](docs/API_DOCS.md) for complete API reference.

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| POST /api/users/auth/ | Login |
| GET /api/schools/schools/ | List schools |
| GET /api/staff/staff/ | List staff |
| GET /api/students/students/ | List students |
| GET /api/files/files/ | List files |
| GET /api/analytics/stats/overview/ | Dashboard stats |

## Deployment

See [Deployment Guide](docs/DEPLOYMENT.md) for production deployment instructions.

### Production Deployment

```bash
# Configure environment
cp .env.production.example .env.production
nano .env.production

# Deploy
./scripts/deploy.sh
```

## Documentation

- [API Documentation](docs/API_DOCS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [User Manual](docs/USER_MANUAL.md)
- [Training Manual](docs/TRAINING_MANUAL.md)

## Security

- JWT Authentication with refresh tokens
- Multi-Factor Authentication (MFA)
- Role-Based Access Control (RBAC)
- Account lockout after 5 failed attempts
- Session timeout (30 min idle)
- IP whitelisting for admin
- Audit logging
- Data encryption

## Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time | < 200ms |
| Page Load Time | < 2.5s |
| System Uptime | 99.9% |
| Concurrent Users | 10,000+ |

## Support

- **Email**: support@ediv.gov.ng
- **Phone**: +234 XXX XXX XXXX
- **Hours**: Monday - Friday, 8:00 AM - 5:00 PM

## License

Copyright © 2024 Education District IV. All rights reserved.

## Acknowledgments

- Lagos State Government
- Ministry of Education
- Education District IV Staff
- All stakeholders who contributed to this project
