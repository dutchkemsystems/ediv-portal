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
