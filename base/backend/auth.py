from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import logging

security = HTTPBearer()

# For demo purposes, we accept a hardcoded DEV_TOKEN or expect IDP validation in prod.
# In a real scenario, this would verify JWTs from Google Identity Platform.
DEV_TOKEN = os.getenv("DEV_TOKEN", "secure-rag-dev-token")

logger = logging.getLogger("uvicorn")

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verifies that the Bearer token matches the expected DEV_TOKEN.
    In production, this would decode and verify a JWT.
    """
    token = credentials.credentials
    if token != DEV_TOKEN:
        logger.warning(f"Failed authentication attempt with token: {token[:4]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
