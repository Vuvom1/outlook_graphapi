# Outlook Email Service API

A FastAPI-based REST API for Microsoft Outlook email operations using OAuth 2.0, Microsoft Graph API, and Dify plugin framework for advanced email management tools.

## 🚀 Features

- **OAuth 2.0 Authentication** with Microsoft Graph API
- **Comprehensive Email Operations**: Read, send, delete, draft, and manage emails
- **Advanced Email Tools**: Built with Dify plugin framework for extensibility
  - Draft email creation and management
  - Email prioritization and flagging
  - Attachment handling for drafts
  - Message updating and formatting
- **Folder Management**: Access different mail folders
- **Search and Filtering**: Advanced email search capabilities
- **Token Management**: Automatic token refresh and validation
- **Code Quality**: Integrated with Ruff for linting and formatting
- **Structured Architecture**: Clean separation of concerns with routers, services, and tools

## 📋 Prerequisites

1. **Azure AD Application Registration**:
   - Register an application in Azure Active Directory
   - Configure redirect URIs and API permissions
   - Required permissions: `Mail.ReadWrite`, `Mail.Send`, `User.Read`
   - Note down Client ID, Client Secret, and Tenant ID

2. **Python Environment**:
   - Python 3.13+ recommended
   - Virtual environment setup

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Vuvom1/outlook_graphapi.git
   cd outlook_graphapi
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Create a `.env` file in the root directory:
   ```env
   AZURE_CLIENT_ID=your-client-id-here
   AZURE_CLIENT_SECRET=your-client-secret-here
   AZURE_TENANT_ID=your-tenant-id-here
   REDIRECT_URI=http://localhost:8000/oauth/callback
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```
   Or use uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, access the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/
- **Detailed Health**: http://localhost:8000/health

## 🔗 API Endpoints

### OAuth Authentication

#### Get Authorization URL
```http
GET /oauth/authorize
```

#### OAuth Callback
```http
GET /oauth/callback?code=...&state=...
```

#### Refresh Token
```http
POST /oauth/refresh
Content-Type: application/json
{
  "refresh_token": "your_refresh_token_here"
}
```

#### Validate Token
```http
POST /oauth/validate
Content-Type: application/json
{
  "access_token": "your_access_token_here"
}
```

### Email Operations

All email endpoints require authentication:
```http
Authorization: Bearer your_access_token_here
```

#### Core Email Operations
- `GET /emails/list` - List emails with filtering options
- `GET /emails/{message_id}` - Get specific email by ID
- `POST /emails/send` - Send a new email
- `POST /emails/drafts` - Create email draft
- `DELETE /emails/{email_id}` - Delete email
- `PATCH /emails/{email_id}` - Update email
- `PATCH /emails/{email_id}/read` - Mark as read/unread
- `PATCH /emails/{email_id}/priority` - Set email priority

#### Draft Management
- `POST /emails/drafts/{draft_id}/attachments` - Add attachments to draft
- `POST /emails/drafts/{draft_id}/send` - Send draft email

#### Folder Operations
- `GET /emails/folders/list` - List all mail folders

### Legacy Endpoints (Deprecated)
- `GET /emails/list-message` - Use `/emails/list` instead
- `GET /emails/get-message` - Use `/emails/{message_id}` instead
- `POST /emails/send-message` - Use `/emails/send` instead

## 🏗️ Project Structure

```
outlook_graphapi/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration (Ruff, etc.)
├── .pylintrc              # Pylint configuration
├── .env                   # Environment variables (create this)
│
├── providers/             # Authentication providers
│   ├── __init__.py
│   └── outlook.py         # Outlook OAuth provider
│
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── oauth.py           # OAuth endpoints
│   └── email.py           # Email endpoints
│
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py    # Authentication services
│   └── email_service.py   # Email operations service
│
├── schemas/               # Pydantic models
│   ├── __init__.py
│   ├── common_schemas.py  # Common response models
│   ├── email_schemas.py   # Email-related models
│   └── oauth_schemas.py   # OAuth models
│
└── tools/                 # Email operation tools (Dify plugin based)
    ├── __init__.py
    ├── base_tool.py       # Base tool class
    ├── draft_message.py   # Draft creation tool
    ├── send_message.py    # Email sending tool
    ├── get_message.py     # Message retrieval tool
    ├── list_message.py    # Message listing tool
    ├── delete_message.py  # Message deletion tool
    ├── update_message.py  # Message update tool
    ├── flag_message.py    # Message flagging tool
    ├── send_draft.py      # Draft sending tool
    ├── prioritize_message_tool.py  # Priority management
    └── add_attachment_to_draft.py  # Attachment handling
```

## 🔧 Development

### Code Quality Tools
This project uses Ruff for linting and formatting:

```bash
# Check code quality
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Running Tests
```bash
# Run tests (when implemented)
python -m pytest test/
```

### Development Mode
```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the main script
python main.py
```

## 💡 Usage Examples

### 1. Complete OAuth Flow
```python
import requests

# 1. Get authorization URL
auth_response = requests.get("http://localhost:8000/oauth/authorize")
auth_url = auth_response.json()["authorization_url"]

# 2. User visits auth_url and authorizes
# 3. Callback returns tokens

# 4. Use access token for API calls
headers = {"Authorization": f"Bearer {access_token}"}
emails = requests.get("http://localhost:8000/emails/list", headers=headers)
```

### 2. Create and Send Draft Email
```python
# Create draft
draft_data = {
    "to": ["recipient@example.com"],
    "subject": "API Test Email",
    "body": "Hello from the Outlook API!",
    "importance": "high"
}
draft_response = requests.post(
    "http://localhost:8000/emails/drafts",
    json=draft_data,
    headers=headers
)

# Send the draft
draft_id = draft_response.json()["result"]
send_response = requests.post(
    f"http://localhost:8000/emails/drafts/{draft_id}/send",
    headers=headers
)
```

## 🛡️ Security Best Practices

1. **Environment Variables**: Never commit `.env` file to version control
2. **HTTPS**: Always use HTTPS in production
3. **Token Security**: Implement secure token storage and refresh logic
4. **CORS**: Configure CORS settings appropriately
5. **Rate Limiting**: Implement rate limiting for production use
6. **Input Validation**: All inputs are validated using Pydantic models

## 🚨 Error Handling

The API provides comprehensive error handling with detailed responses:

```json
{
  "error": "Authentication failed",
  "message": "Invalid access token",
  "timestamp": "2025-08-21T10:30:00Z"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created (for drafts, etc.)
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## 📈 Future Enhancements

- [ ] Multi-user support with user session management
- [ ] Email templates and bulk operations
- [ ] Advanced search with full-text indexing
- [ ] Real-time notifications via WebSocket
- [ ] Calendar integration
- [ ] Email analytics and reporting
- [ ] Docker containerization
- [ ] Database integration for caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run code quality checks (`ruff check .` && `ruff format .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [API documentation](http://localhost:8000/docs)
2. Review the error messages and logs
3. Open an issue on GitHub with detailed information

---

**Built with ❤️ using FastAPI, Microsoft Graph API, and modern Python practices**
