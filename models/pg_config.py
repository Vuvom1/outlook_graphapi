"""
PostgreSQL database configuration and connection management.
"""

import os
from typing import Optional
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

# PostgreSQL Configuration
DATABASE_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "outlook_api"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password")
}

# Connection URL for asyncpg
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"


class DatabaseConnection:
    """PostgreSQL database connection manager."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize_pool(self):
        """Initialize the connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise
    
    async def close_pool(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")
    
    def get_sync_connection(self):
        """Get a synchronous connection for migrations and setup."""
        return psycopg2.connect(
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            database=DATABASE_CONFIG["database"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            cursor_factory=RealDictCursor
        )


# Global database connection instance
db_connection = DatabaseConnection()


async def get_db_pool() -> asyncpg.Pool:
    """Get the database connection pool."""
    if not db_connection.pool:
        await db_connection.initialize_pool()
    return db_connection.pool
