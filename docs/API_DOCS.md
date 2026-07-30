# Education District IV Portal - API Documentation

## Overview

This document provides comprehensive API documentation for the Education District IV Portal.

## Base URL

```
Development: http://localhost:8000/api
Production: https://your-domain.com/api
```

## Authentication

All API endpoints require JWT authentication except for the login endpoint.

### Login

```http
POST /api/users/auth/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "SYSADMIN"
  }
}
```

### Refresh Token

```http
POST /api/users/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using Authentication

Include the access token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

## API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users/users/ | List all users |
| POST | /api/users/users/ | Create a new user |
| GET | /api/users/users/{id}/ | Get user details |
| PUT | /api/users/users/{id}/ | Update user |
| DELETE | /api/users/users/{id}/ | Delete user |
| GET | /api/users/users/me/ | Get current user profile |
| POST | /api/users/users/change_password/ | Change password |

### Schools

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/schools/schools/ | List all schools |
| POST | /api/schools/schools/ | Create a new school |
| GET | /api/schools/schools/{id}/ | Get school details |
| PUT | /api/schools/schools/{id}/ | Update school |
| DELETE | /api/schools/schools/{id}/ | Delete school |

### Staff

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/staff/staff/ | List all staff |
| POST | /api/staff/staff/ | Create a new staff |
| GET | /api/staff/staff/{id}/ | Get staff details |
| PUT | /api/staff/staff/{id}/ | Update staff |
| DELETE | /api/staff/staff/{id}/ | Delete staff |
| GET | /api/staff/leaves/ | List leave requests |
| POST | /api/staff/leaves/ | Create leave request |
| GET | /api/staff/performances/ | List performance records |

### Students

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/students/students/ | List all students |
| POST | /api/students/students/ | Create a new student |
| GET | /api/students/students/{id}/ | Get student details |
| PUT | /api/students/students/{id}/ | Update student |
| DELETE | /api/students/students/{id}/ | Delete student |

### Academics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/academics/classes/ | List all classes |
| POST | /api/academics/classes/ | Create a new class |
| GET | /api/academics/subjects/ | List all subjects |
| POST | /api/academics/subjects/ | Create a new subject |
| GET | /api/academics/exams/ | List all exams |
| POST | /api/academics/exams/ | Create a new exam |
| GET | /api/academics/exam-results/ | List exam results |
| POST | /api/academics/exam-results/ | Create exam result |
| GET | /api/academics/report-cards/ | List report cards |
| GET | /api/academics/calendar/ | List academic calendar |
| GET | /api/academics/enrollments/ | List enrollments |

### Attendance

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/attendance/student-attendance/ | List student attendance |
| POST | /api/attendance/student-attendance/ | Record attendance |
| GET | /api/attendance/staff-attendance/ | List staff attendance |
| POST | /api/attendance/staff-attendance/ | Record staff attendance |

### Finance

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/finance/fee-structures/ | List fee structures |
| POST | /api/finance/fee-structures/ | Create fee structure |
| GET | /api/finance/student-fees/ | List student fees |
| GET | /api/finance/payments/ | List payments |
| POST | /api/finance/payments/ | Record payment |
| GET | /api/finance/budgets/ | List budgets |

### Files (E-Registry)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/files/files/ | List all files |
| POST | /api/files/files/ | Create a new file |
| GET | /api/files/files/{id}/ | Get file details |
| PUT | /api/files/files/{id}/ | Update file |
| DELETE | /api/files/files/{id}/ | Delete file |
| GET | /api/files/movements/ | List file movements |
| POST | /api/files/movements/ | Record file movement |

### Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/workflows/workflows/ | List all workflows |
| POST | /api/workflows/workflows/ | Create a new workflow |
| GET | /api/workflows/instances/ | List workflow instances |
| GET | /api/workflows/tasks/ | List tasks |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/reports/reports/ | List all reports |
| POST | /api/reports/reports/ | Create a report |
| GET | /api/reports/reports/{id}/ | Get report details |
| GET | /api/reports/dashboards/ | List dashboards |
| GET | /api/reports/widgets/ | List widgets |
| POST | /api/reports/reports/{id}/export/ | Export report |
| POST | /api/reports/import_data/ | Import data |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/analytics/stats/overview/ | Get overview statistics |
| GET | /api/analytics/stats/school_stats/ | Get school statistics |
| GET | /api/analytics/stats/enrollment_stats/ | Get enrollment statistics |
| GET | /api/analytics/stats/attendance_stats/ | Get attendance statistics |
| GET | /api/analytics/stats/financial_stats/ | Get financial statistics |
| GET | /api/analytics/stats/recent_activity/ | Get recent activity |
| GET | /api/analytics/reports/ | List analytics reports |
| GET | /api/analytics/kpis/ | List KPIs |

### HR

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/hr/job-postings/ | List job postings |
| POST | /api/hr/job-postings/ | Create job posting |
| GET | /api/hr/applications/ | List job applications |
| GET | /api/hr/payroll-periods/ | List payroll periods |
| GET | /api/hr/payslips/ | List payslips |

### Communication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/communication/messages/ | List messages |
| GET | /api/communication/conversations/ | List conversations |
| GET | /api/communication/circulars/ | List circulars |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/notifications/notifications/ | List notifications |
| PUT | /api/notifications/notifications/{id}/ | Mark as read |

### Departments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/departments/departments/ | List departments |
| POST | /api/departments/departments/ | Create department |
| GET | /api/departments/units/ | List department units |

### Registry (E-Registry)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/registry/documents/ | List documents |
| POST | /api/registry/documents/ | Create document |
| GET | /api/registry/correspondences/ | List correspondences |
| GET | /api/registry/memos/ | List memos |

### Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/workflows/workflows/ | List all workflows |
| POST | /api/workflows/workflows/ | Create a new workflow |
| GET | /api/workflows/instances/ | List workflow instances |
| GET | /api/workflows/tasks/ | List tasks |

### Inspection

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/inspection/inspections/ | List inspections |
| POST | /api/inspection/inspections/ | Create inspection |
| GET | /api/inspection/checklists/ | List checklists |
| GET | /api/inspection/actions/ | List inspection actions |

### Library

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/library/books/ | List books |
| POST | /api/library/books/ | Add book |
| GET | /api/library/loans/ | List book loans |
| POST | /api/library/loans/ | Checkout book |

### Transport

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/transport/vehicles/ | List vehicles |
| POST | /api/transport/vehicles/ | Add vehicle |
| GET | /api/transport/routes/ | List bus routes |
| POST | /api/transport/routes/ | Create route |

### CPD (Professional Development)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/cpd/activities/ | List CPD activities |
| GET | /api/cpd/records/ | List CPD records |

### Wellness

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/wellness/counseling-sessions/ | List counseling sessions |
| GET | /api/wellness/check-ins/ | List wellness check-ins |
| GET | /api/wellness/resources/ | List wellness resources |

### Alumni

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/alumni/members/ | List alumni members |
| GET | /api/alumni/events/ | List alumni events |
| GET | /api/alumni/donations/ | List alumni donations |

### Assets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/assets/assets/ | List assets |
| POST | /api/assets/assets/ | Register asset |
| GET | /api/assets/maintenance/ | List maintenance records |

### Discipline

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/discipline/incidents/ | List incidents |
| POST | /api/discipline/incidents/ | Report incident |
| GET | /api/discipline/behavior-plans/ | List behavior plans |

### Co-Curricular

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/co-curricular/activities/ | List activities |
| GET | /api/co-curricular/competitions/ | List competitions |

### French Unit

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/french/programs/ | List French programs |
| GET | /api/french/clubs/ | List French clubs |

### E-Learning

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/e-learning/courses/ | List courses |
| POST | /api/e-learning/courses/ | Create course |

### Parent-Teacher

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/parent-teacher/meetings/ | List PTA meetings |
| GET | /api/parent-teacher/conferences/ | List conferences |

### Timetable

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/timetable/periods/ | List periods |
| POST | /api/timetable/periods/ | Create period |
| GET | /api/timetable/timetables/ | List timetables |

### Infrastructure

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/infrastructure/facilities/ | List facilities |
| GET | /api/infrastructure/maintenance-requests/ | List maintenance requests |
| GET | /api/infrastructure/projects/ | List projects |

### Data Import/Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/data-import-export/jobs/ | List import jobs |

### Mail Workflow

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/mail-workflow/incoming-mail/ | List incoming mail |
| GET | /api/mail-workflow/outgoing-mail/ | List outgoing mail |
| GET | /api/mail-workflow/correspondences/ | List correspondences |

### Audit

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/audit/logs/ | List audit logs |
| GET | /api/audit/compliance-items/ | List compliance items |
| GET | /api/audit/violations/ | List violations |

## Query Parameters

Most list endpoints support the following query parameters:

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)
- `search` - Search term
- `ordering` - Sort field (prefix with `-` for descending)

### Filtering

Many endpoints support filtering by specific fields:

```
GET /api/schools/schools/?school_type=SENIOR&lga=APAPA
GET /api/staff/staff/?category=TEACHING&is_active=true
GET /api/students/students/?school=1&status=ACTIVE
```

## Error Responses

```json
{
  "success": false,
  "error": {
    "status_code": 400,
    "message": {
      "field_name": ["Error message"]
    }
  }
}
```

## Rate Limiting

- Anonymous: 100 requests per hour
- Authenticated: 1000 requests per hour

## Pagination

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/schools/schools/?page=2",
  "previous": null,
  "results": [...]
}
```
