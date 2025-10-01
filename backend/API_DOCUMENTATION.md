# GWorkspace Analyzer API Documentation

## Base URL
```
http://localhost:8000
```

## API Endpoints

### Health & Info

#### `GET /`
Root endpoint with API information
```json
{
  "message": "Welcome to GWorkspace Analyzer API",
  "version": "1.0.0",
  "docs": "/api/docs"
}
```

#### `GET /health`
Health check endpoint
```json
{
  "status": "healthy",
  "service": "GWorkspace Analyzer API",
  "version": "1.0.0"
}
```

---

## Authentication Endpoints (`/api/v1/auth`)

### `GET /api/v1/auth/google/login`
Initiate Google OAuth flow

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

**Usage:**
1. Frontend redirects user to `auth_url`
2. User grants permissions
3. Google redirects back with authorization code

### `POST /api/v1/auth/google/callback`
Handle Google OAuth callback

**Request Body:**
```json
{
  "code": "authorization_code_from_google",
  "redirect_uri": "http://localhost:3000/auth/callback"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Note:** Currently returns 501 for new users. Use Supabase client-side auth for user creation.

### `POST /api/v1/auth/refresh`
Refresh access token

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "access_token": "new_token...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### `GET /api/v1/auth/me`
Get current user info

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "user_uuid",
  "email": "user@example.com",
  "org_id": "org_uuid",
  "preferences": {...},
  "last_scan_at": "2024-03-15T10:30:00",
  "scan_count": 5
}
```

---

## Scan Job Endpoints (`/api/v1/scan`)

### `POST /api/v1/scan/start`
Start a new Gmail scan job

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-03-31"
}
```

**Response (201 Created):**
```json
{
  "id": "scan_job_uuid",
  "user_id": "user_uuid",
  "org_id": "org_uuid",
  "status": "queued",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "total_emails": 0,
  "processed_emails": 0,
  "invoices_found": 0,
  "error_message": null,
  "started_at": null,
  "completed_at": null,
  "created_at": "2024-03-15T10:30:00"
}
```

**Errors:**
- `409 Conflict`: Scan already in progress
- `400 Bad Request`: Invalid date range

### `GET /api/v1/scan/jobs`
List user's scan jobs

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `limit` (default: 10): Maximum number of jobs to return

**Response:**
```json
[
  {
    "id": "scan_job_uuid",
    "status": "completed",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "invoices_found": 127,
    ...
  }
]
```

### `GET /api/v1/scan/jobs/{job_id}`
Get scan job details

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** Same as POST /scan/start

### `DELETE /api/v1/scan/jobs/{job_id}`
Cancel a queued or processing scan job

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** 204 No Content

**Errors:**
- `404 Not Found`: Job not found
- `400 Bad Request`: Cannot cancel completed/failed job

---

## Invoice Endpoints (`/api/v1/invoices`)

### `GET /api/v1/invoices`
List invoices with filters and pagination

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page` (default: 1): Page number
- `page_size` (default: 20, max: 100): Items per page
- `vendor`: Filter by vendor name
- `start_date`: Filter by invoice_date >= start_date
- `end_date`: Filter by invoice_date <= end_date
- `min_amount`: Filter by amount >= min_amount
- `max_amount`: Filter by amount <= max_amount

**Response:**
```json
{
  "invoices": [
    {
      "id": "invoice_uuid",
      "vendor_name": "Amazon Web Services",
      "vendor_name_normalized": "amazonwebservices",
      "invoice_number": "INV-2024-001",
      "amount": 1250.00,
      "currency": "USD",
      "invoice_date": "2024-03-01",
      "due_date": "2024-03-15",
      "confidence_score": 0.95,
      "extraction_method": "pdf_parser",
      ...
    }
  ],
  "total": 127,
  "page": 1,
  "page_size": 20
}
```

### `GET /api/v1/invoices/{invoice_id}`
Get single invoice details

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** Invoice object

### `GET /api/v1/invoices/vendors/list`
Get list of vendors with aggregated data

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": "vendor_uuid",
    "name": "Amazon Web Services",
    "name_normalized": "amazonwebservices",
    "total_invoices": 12,
    "total_spent": 15000.00,
    "avg_invoice_amount": 1250.00,
    "is_subscription": true,
    "billing_frequency": "monthly",
    ...
  }
]
```

### `GET /api/v1/invoices/stats/summary`
Get invoice statistics summary

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "total_invoices": 127,
  "total_amount": 45230.50,
  "currency": "USD",
  "monthly_totals": {
    "2024-01": 15000.00,
    "2024-02": 16500.00,
    "2024-03": 13730.50
  }
}
```

### `DELETE /api/v1/invoices/{invoice_id}`
Delete an invoice

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** 204 No Content

---

## Findings Endpoints (`/api/v1/findings`)

### `GET /api/v1/findings/summary`
Get summary of all findings

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "pending_count": 15,
  "resolved_count": 8,
  "ignored_count": 3,
  "total_guaranteed_waste": 1500.00,
  "total_potential_waste": 49.00,
  "by_type": {
    "duplicate": {
      "count": 12,
      "pending": 10,
      "total_amount": 1250.00
    },
    "price_increase": {
      "count": 4,
      "pending": 3,
      "total_amount": 250.00
    }
  }
}
```

**Note:**
- `total_guaranteed_waste`: Exact duplicates + price increases (high confidence)
- `total_potential_waste`: Probable duplicates (requires user review)

### `GET /api/v1/findings`
List findings with filters and pagination

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page` (default: 1): Page number
- `page_size` (default: 20, max: 100): Items per page
- `status`: Filter by status (pending, resolved, ignored)
- `type`: Filter by type (duplicate, price_increase, etc.)

**Response:**
```json
{
  "findings": [
    {
      "id": "finding_uuid",
      "type": "duplicate",
      "status": "pending",
      "title": "Duplicate charge from Amazon Web Services",
      "description": "Same invoice charged 2 times (exact match)",
      "amount": 1250.00,
      "currency": "USD",
      "confidence_score": 0.98,
      "details": {
        "invoice_number": "INV-2024-001",
        "charge_amount": 1250.00,
        "charged_times": 2,
        "dates": ["2024-03-01", "2024-03-02"]
      },
      "created_at": "2024-03-15T10:30:00",
      ...
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

### `GET /api/v1/findings/{finding_id}`
Get single finding details

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** Finding object

### `GET /api/v1/findings/{finding_id}/invoices`
Get invoices related to a finding

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** Array of invoice objects

### `PATCH /api/v1/findings/{finding_id}`
Update finding status (resolve or ignore)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "status": "resolved",
  "user_notes": "Contacted vendor, refund issued"
}
```

**Response:** Updated finding object

**Status values:**
- `resolved`: User has resolved the issue
- `ignored`: User has marked as not an issue
- `pending`: Reset to pending

### `DELETE /api/v1/findings/{finding_id}`
Delete a finding (admin only)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** 204 No Content

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "start_date"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Authentication Flow

1. **Frontend calls** `GET /api/v1/auth/google/login`
2. **Frontend redirects** user to `auth_url`
3. **User grants permissions** on Google
4. **Google redirects** to `redirect_uri` with authorization code
5. **Frontend calls** `POST /api/v1/auth/google/callback` with code
6. **Backend returns** JWT access token
7. **Frontend stores** token in localStorage/cookie
8. **Frontend includes** token in `Authorization: Bearer {token}` header for all API calls

---

## Typical Usage Flow

### 1. Authentication
```
GET /api/v1/auth/google/login
→ Redirect to Google
→ POST /api/v1/auth/google/callback
→ Receive JWT token
```

### 2. Start Scan
```
POST /api/v1/scan/start
{
  "start_date": "2024-01-01",
  "end_date": "2024-03-31"
}
→ Scan job created (queued)
```

### 3. Monitor Scan Progress
```
GET /api/v1/scan/jobs/{job_id}
→ status: "processing"
→ processed_emails: 50/200
```

### 4. View Results
```
GET /api/v1/findings/summary
→ total_guaranteed_waste: $1,500

GET /api/v1/findings?status=pending
→ List of issues to review

GET /api/v1/invoices?page=1
→ List of scanned invoices
```

### 5. Take Action
```
PATCH /api/v1/findings/{finding_id}
{
  "status": "resolved",
  "user_notes": "Contacted vendor, refund issued"
}
```

---

## Interactive API Documentation

Visit **http://localhost:8000/api/docs** for Swagger UI with interactive API testing.

Visit **http://localhost:8000/api/redoc** for ReDoc documentation.
