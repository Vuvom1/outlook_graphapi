"""
Outlook Email Service API - Main FastAPI Application
"""
# IMPORTANT: Suppress gevent monkey-patching warnings and patch early
import warnings
warnings.filterwarnings("ignore", message=".*Monkey-patching ssl.*", category=Warning)

import gevent.monkey
gevent.monkey.patch_all(ssl=False, subprocess=False)  # Patch selectively to avoid conflicts

import os
import logging
from typing import Any
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import SYSTEM_CREDENTIALS, REDIRECT_URI
from routers.oauth import oauth_router
from routers.email import email_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Outlook Email Service API",
    description="A REST API for Microsoft Outlook email operations using OAuth 2.0 and Microsoft Graph API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(oauth_router, tags=["OAuth Authentication"])
app.include_router(email_router, tags=["Email Operations"])


@app.get("/", summary="Health Check")
async def root():
    """Health check endpoint."""
    return {
        "service": "Outlook Email Service API",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "oauth": "/oauth",
            "emails": "/emails"
        }
    }


@app.get("/health", summary="Detailed Health Check")
async def health_check():
    """Detailed health check with system information."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "Outlook Email Service API",
        "version": "1.0.0",
        "components": {
            "oauth": "operational",
            "email_service": "operational",
            "microsoft_graph": "operational"
        },
        "configuration": {
            "redirect_uri": REDIRECT_URI,
            "client_configured": bool(SYSTEM_CREDENTIALS.get("client_id")),
            "tenant_id": SYSTEM_CREDENTIALS.get("tenant_id", "common")
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


def main():
    """Main function to run the FastAPI application."""
    import uvicorn
    
    logger.info("Starting Outlook Email Service API...")
    logger.info("Available endpoints:")
    logger.info("- Health Check: http://localhost:8000/")
    logger.info("- API Documentation: http://localhost:8000/docs")
    logger.info("- OAuth Authorization: http://localhost:8000/oauth/authorize")
    logger.info("- Email Operations: http://localhost:8000/emails")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()

