# 🐘 PostgreSQL Migration Guide

## ✅ **Migration Complete!**

Your Outlook API has been successfully converted from **SQLite** to **PostgreSQL**!

### 🔄 **What Changed**

#### **Database Migration:**
- ✅ **From**: SQLite file-based database (`credentials.db`)
- ✅ **To**: PostgreSQL server database
- ✅ **Tables**: Same schema (user_credentials, user_sessions, api_keys)
- ✅ **Features**: All authentication functionality preserved

#### **New Components:**
1. **PostgreSQL Docker Container** - Runs locally on port 5432
2. **pgAdmin Web Interface** - Database management on port 5050
3. **Connection Pooling** - Improved performance and reliability
4. **Production-Ready** - Scalable database solution

### 🚀 **Quick Start**

#### **1. Start PostgreSQL:**
```bash
# Setup and start PostgreSQL
./setup_postgres.sh
```

#### **2. Start API Server:**
```bash
# Start with HTTPS
.venv/bin/python -m uvicorn main:app --reload --ssl-keyfile=certs/key.pem --ssl-certfile=certs/cert.pem
```

#### **3. Test OAuth Flow:**
Visit: https://localhost:8000/client

### 📋 **Environment Configuration**

Your `.env` file now includes PostgreSQL settings:

```bash
# PostgreSQL Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=outlook_api
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Azure OAuth (your existing settings)
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-secret
REDIRECT_URI=https://localhost:8000/client/callback
```

### 🛠️ **Database Management**

#### **PostgreSQL Access:**
- **Connection**: localhost:5432
- **Database**: outlook_api
- **Username**: postgres
- **Password**: password

#### **pgAdmin Web Interface:**
- **URL**: http://localhost:5050
- **Email**: admin@outlook-api.com
- **Password**: admin

#### **Docker Commands:**
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Stop PostgreSQL
docker-compose down

# View logs
docker-compose logs postgres

# Access PostgreSQL CLI
docker-compose exec postgres psql -U postgres -d outlook_api
```

### 📊 **Database Schema**

Same tables, now in PostgreSQL:

```sql
-- User OAuth credentials
user_credentials (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    display_name VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Web session tokens
user_sessions (
    id SERIAL PRIMARY KEY,
    session_token VARCHAR(255) UNIQUE,
    user_id VARCHAR(255) REFERENCES user_credentials(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- API keys for programmatic access
api_keys (
    id SERIAL PRIMARY KEY,
    api_key VARCHAR(255) UNIQUE,
    user_id VARCHAR(255) REFERENCES user_credentials(user_id),
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 🔧 **Key Improvements**

#### **Performance:**
- **Connection Pooling**: Multiple concurrent requests
- **Indexes**: Optimized queries
- **ACID Compliance**: Data integrity guaranteed

#### **Scalability:**
- **Multi-User Support**: Handles concurrent users
- **Production Ready**: Can scale beyond development
- **Backup/Restore**: Standard PostgreSQL tools

#### **Development:**
- **pgAdmin**: Visual database management
- **SQL Queries**: Advanced query capabilities
- **Monitoring**: Built-in PostgreSQL metrics

### ⚡ **Migration Benefits**

#### **For Development:**
- **Better Debugging**: SQL query analysis
- **Data Management**: Visual tools (pgAdmin)
- **Testing**: Isolated test databases

#### **For Production:**
- **Concurrent Users**: Multiple simultaneous OAuth flows
- **Data Integrity**: ACID transactions
- **Backup Strategy**: Built-in PostgreSQL backup tools
- **Monitoring**: Database performance metrics

### 🎯 **OAuth Flow (Unchanged)**

The OAuth authentication flow remains exactly the same:

1. **User Authorization**: https://localhost:8000/client
2. **Microsoft OAuth**: User grants permissions
3. **Callback Processing**: https://localhost:8000/client/callback?code=...
4. **Credential Storage**: Now saved to PostgreSQL
5. **API Access**: Same session/API key authentication

### 📁 **Project Structure**

```
outlook_graphapi/
├── models/
│   ├── database.py          # PostgreSQL implementation
│   └── pg_config.py         # PostgreSQL connection config
├── docker-compose.yml       # PostgreSQL container setup
├── setup_postgres.sh        # Database setup script
├── init.sql                 # Database initialization
└── requirements.txt         # Updated with PostgreSQL deps
```

### 🚨 **Important Notes**

1. **Data Migration**: Existing SQLite data needs manual migration if required
2. **Environment**: Update .env with PostgreSQL credentials
3. **Docker Required**: PostgreSQL runs in Docker container
4. **Port 5432**: Make sure port is available
5. **Authentication**: All OAuth flows work identically

### 🎉 **You're Ready!**

Your Outlook API now uses PostgreSQL for:
- ✅ **User credential storage**
- ✅ **Session management** 
- ✅ **API key generation**
- ✅ **OAuth token persistence**

**Start the database and enjoy production-ready OAuth authentication!** 🚀
