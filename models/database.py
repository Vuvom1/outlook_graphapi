"""
Database models for user authentication and credential storage using PostgreSQL.
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import json
import secrets
import logging

try:
    import asyncpg
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    asyncpg = None
    psycopg2 = None
    RealDictCursor = None

logger = logging.getLogger(__name__)

# PostgreSQL Configuration
DATABASE_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "outlook_api"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password123")
}

DATABASE_URL = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"


class UserCredentialsDB:
    """Database manager for user credentials and authentication using PostgreSQL."""
    
    def __init__(self):
        self.pool = None
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL packages not available. Install with: pip install psycopg2-binary asyncpg")
        
        conn = None
        try:
            # Create synchronous connection for schema setup
            conn = psycopg2.connect(
                host=DATABASE_CONFIG["host"],
                port=DATABASE_CONFIG["port"],
                database=DATABASE_CONFIG["database"],
                user=DATABASE_CONFIG["user"],
                password=DATABASE_CONFIG["password"]
            )
            
            with conn.cursor() as cursor:
                # Create user_credentials table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_credentials (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) UNIQUE NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        display_name VARCHAR(255),
                        access_token TEXT NOT NULL,
                        refresh_token TEXT,
                        token_expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Create user_sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id SERIAL PRIMARY KEY,
                        session_token VARCHAR(255) UNIQUE NOT NULL,
                        user_id VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES user_credentials (user_id)
                    )
                """)
                
                # Create api_keys table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id SERIAL PRIMARY KEY,
                        api_key VARCHAR(255) UNIQUE NOT NULL,
                        user_id VARCHAR(255) NOT NULL,
                        name VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES user_credentials (user_id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON user_credentials(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_token ON user_sessions(session_token)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_key ON api_keys(api_key)")
                
                conn.commit()
                logger.info("PostgreSQL database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL database: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _get_connection(self):
        """Get a synchronous database connection."""
        return psycopg2.connect(
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            database=DATABASE_CONFIG["database"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            cursor_factory=RealDictCursor
        )
    
    def save_user_credentials(self, user_info: Dict, tokens: Dict) -> str:
        """Save user credentials after OAuth exchange."""
        user_id = user_info.get('id') or user_info.get('userPrincipalName', '').split('@')[0]
        email = user_info.get('mail') or user_info.get('userPrincipalName', '')
        display_name = user_info.get('displayName', '')
        
        expires_at = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_credentials 
                    (user_id, email, display_name, access_token, refresh_token, token_expires_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) DO UPDATE SET
                        email = EXCLUDED.email,
                        display_name = EXCLUDED.display_name,
                        access_token = EXCLUDED.access_token,
                        refresh_token = EXCLUDED.refresh_token,
                        token_expires_at = EXCLUDED.token_expires_at,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    user_id, 
                    email, 
                    display_name, 
                    tokens['access_token'],
                    tokens.get('refresh_token'),
                    expires_at
                ))
                conn.commit()
        
        logger.info(f"Saved credentials for user: {email}")
        return user_id
    
    def create_session(self, user_id: str, duration_hours: int = 24) -> str:
        """Create a new session token for a user."""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_sessions (session_token, user_id, expires_at)
                    VALUES (%s, %s, %s)
                """, (session_token, user_id, expires_at))
                conn.commit()
        
        logger.info(f"Created session for user: {user_id}")
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate a session token and return user info."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT s.user_id, s.expires_at, u.email, u.display_name, u.access_token, u.token_expires_at
                    FROM user_sessions s
                    JOIN user_credentials u ON s.user_id = u.user_id
                    WHERE s.session_token = %s AND s.is_active = TRUE AND u.is_active = TRUE
                """, (session_token,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Check if session is expired
                if row['expires_at'] < datetime.utcnow():
                    self.invalidate_session(session_token)
                    return None
                
                return {
                    'user_id': row['user_id'],
                    'email': row['email'],
                    'display_name': row['display_name'],
                    'access_token': row['access_token'],
                    'token_expires_at': row['token_expires_at'].isoformat() if row['token_expires_at'] else None
                }
    
    def generate_api_key(self, user_id: str, name: str = "Default") -> str:
        """Generate a new API key for a user."""
        api_key = f"ok_{secrets.token_urlsafe(40)}"
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_keys (api_key, user_id, name)
                    VALUES (%s, %s, %s)
                """, (api_key, user_id, name))
                conn.commit()
        
        logger.info(f"Generated API key for user: {user_id}")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate an API key and return user credentials."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT a.user_id, u.email, u.display_name, u.access_token, u.token_expires_at, u.refresh_token
                    FROM api_keys a
                    JOIN user_credentials u ON a.user_id = u.user_id
                    WHERE a.api_key = %s AND a.is_active = TRUE AND u.is_active = TRUE
                """, (api_key,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Update last used timestamp
                cursor.execute("""
                    UPDATE api_keys SET last_used_at = CURRENT_TIMESTAMP 
                    WHERE api_key = %s
                """, (api_key,))
                conn.commit()
                
                return {
                    'user_id': row['user_id'],
                    'email': row['email'],
                    'display_name': row['display_name'],
                    'access_token': row['access_token'],
                    'refresh_token': row['refresh_token'],
                    'token_expires_at': row['token_expires_at'].isoformat() if row['token_expires_at'] else None
                }
    
    def get_user_credentials(self, user_id: str) -> Optional[Dict]:
        """Get user credentials by user ID."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM user_credentials 
                    WHERE user_id = %s AND is_active = TRUE
                """, (user_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return dict(row)
    
    def update_tokens(self, user_id: str, access_token: str, refresh_token: str = None, expires_in: int = 3600):
        """Update user tokens after refresh."""
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                if refresh_token:
                    cursor.execute("""
                        UPDATE user_credentials 
                        SET access_token = %s, refresh_token = %s, token_expires_at = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                    """, (access_token, refresh_token, expires_at, user_id))
                else:
                    cursor.execute("""
                        UPDATE user_credentials 
                        SET access_token = %s, token_expires_at = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                    """, (access_token, expires_at, user_id))
                conn.commit()
    
    def invalidate_session(self, session_token: str):
        """Invalidate a session token."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE user_sessions SET is_active = FALSE 
                    WHERE session_token = %s
                """, (session_token,))
                conn.commit()
    
    def revoke_api_key(self, api_key: str):
        """Revoke an API key."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE api_keys SET is_active = FALSE 
                    WHERE api_key = %s
                """, (api_key,))
                conn.commit()
    
    def list_user_api_keys(self, user_id: str) -> List[Dict]:
        """List all API keys for a user."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT api_key, name, created_at, last_used_at, is_active
                    FROM api_keys 
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                
                return [dict(row) for row in cursor.fetchall()]


# Global database instance
credentials_db = UserCredentialsDB()
