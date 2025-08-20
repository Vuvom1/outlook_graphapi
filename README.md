# Outlook Email Service API

A FastAPI-based REST API for Microsoft Outlook email operations using OAuth 2.0 and Microsoft Graph API.

## Features

- **OAuth 2.0 Authentication** with Microsoft Graph API
- **Email Operations**: Read, send, delete, and manage emails
- **Folder Management**: Access different mail folders
- **Attachment Support**: List and download email attachments
- **Search and Filtering**: Advanced email search capabilities
- **Token Management**: Automatic token refresh and validation

## Prerequisites

1. **Azure AD Application Registration**:
   - Register an application in Azure Active Directory
   - Configure redirect URIs
   - Note down Client ID, Client Secret, and Tenant ID

2. **Environment Variables**:
   Create a `.env` file with:
   ```env
   AZURE_CLIENT_ID=your-client-id-here
   AZURE_CLIENT_SECRET=your-client-secret-here
   AZURE_TENANT_ID=your-tenant-id-here
   REDIRECT_URI=http://localhost:8000/oauth/callback
   ```

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### OAuth Authentication

#### 1. Get Authorization URL
```http
GET /oauth/authorize
```
Returns the Microsoft OAuth authorization URL that users should visit to grant permissions.

**Response**:
```json
{
  "authorization_url": "https://login.microsoftonline.com/...",
  "redirect_uri": "http://localhost:8000/oauth/callback",
  "message": "Visit the authorization_url to grant permissions..."
}
```

#### 2. OAuth Callback
```http
GET /oauth/callback?code=...&state=...
```
Handles the OAuth callback and exchanges the authorization code for access tokens.

**Response**:
```json
{
  "message": "OAuth authorization successful",
  "access_token": "...",
  "refresh_token": "...",
  "expires_at": 1640995200,
  "token_type": "Bearer"
}
```

#### 3. Refresh Token
```http
POST /oauth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token_here"
}
```

#### 4. Validate Token
```http
POST /oauth/validate
Content-Type: application/json

{
  "access_token": "your_access_token_here"
}
```

### Email Operations

All email endpoints require an `Authorization` header with the Bearer token:
```http
Authorization: Bearer your_access_token_here
```

#### 1. Get User Profile
```http
GET /emails/me
```

#### 2. List Emails
```http
GET /emails/?folder=inbox&limit=20&offset=0
```

**Query Parameters**:
- `folder`: Email folder (default: "inbox")
- `limit`: Number of emails (1-100, default: 20)
- `offset`: Skip emails (default: 0)
- `search`: Search query
- `from_email`: Filter by sender
- `subject_contains`: Filter by subject
- `is_read`: Filter by read status
- `has_attachments`: Filter by attachments

#### 3. Get Email Details
```http
GET /emails/{email_id}?include_body=true
```

#### 4. Send Email
```http
POST /emails/send
Content-Type: application/json

{
  "to": ["recipient@example.com"],
  "cc": ["cc@example.com"],
  "subject": "Subject",
  "body": "Email body content",
  "is_html": false
}
```

#### 5. Mark as Read/Unread
```http
PATCH /emails/{email_id}/read?is_read=true
```

#### 6. Delete Email
```http
DELETE /emails/{email_id}
```

#### 7. Get Attachments
```http
GET /emails/{email_id}/attachments
```

#### 8. List Folders
```http
GET /emails/folders/list
```

## Usage Example

### 1. Start OAuth Flow
```bash
curl http://localhost:8000/oauth/authorize
```

### 2. Visit the returned authorization URL in browser

### 3. After authorization, use the access token:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/emails/me
```

### 4. List emails:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     "http://localhost:8000/emails/?limit=10&folder=inbox"
```

### 5. Send an email:
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "to": ["recipient@example.com"],
       "subject": "Test Email",
       "body": "Hello from the API!",
       "is_html": false
     }' \
     http://localhost:8000/emails/send
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive credentials to version control
2. **HTTPS in Production**: Use HTTPS for production deployments
3. **CORS Configuration**: Configure CORS appropriately for your domain
4. **Token Storage**: Store tokens securely on the client side
5. **Token Expiration**: Implement proper token refresh logic

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (invalid or expired token)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include detailed error messages:
```json
{
  "detail": "Error description",
  "error": "error_type",
  "timestamp": "2023-12-31T23:59:59Z"
}
```

## Development

### Project Structure
```
outlook_demo/
├── app.py                 # Main FastAPI application
├── main.py               # Entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── providers/
│   └── outlook.py        # Outlook OAuth provider
└── routers/
    ├── __init__.py
    ├── oauth.py          # OAuth endpoints
    └── email.py          # Email endpoints
```

### Running in Development Mode
```bash
# With auto-reload
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Or using the main script
python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
