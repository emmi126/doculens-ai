"""Auth0 authentication service"""
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Optional
import requests
from datetime import datetime

from config import settings
from database import get_db
from models import User

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

DEV_AUTH_TOKEN = "mock-dev-token"
DEV_AUTH0_USER = {
    "sub": "dev-user-123",
    "email": "dev@example.com",
    "name": "Dev User",
    "picture": None,
    "email_verified": True,
}


def is_demo_token(token: str) -> bool:
    """Allow the frontend mock token only in local debug mode."""
    return bool(settings.debug and token == DEV_AUTH_TOKEN)


def get_or_create_user_from_token(token: str, db: Session) -> User:
    """Resolve either the local demo token or a real Auth0 JWT to a DB user."""
    auth0_user = DEV_AUTH0_USER if is_demo_token(token) else verify_token(token)
    user = User.get_or_create_from_auth0(db, auth0_user)
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def get_jwks():
    """Fetch Auth0 public keys for JWT verification"""
    jwks_url = f'https://{settings.auth0_domain}/.well-known/jwks.json'
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()


def verify_token(token: str) -> dict:
    """Verify Auth0 JWT token"""
    try:
        # Get public key from Auth0
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)

        # Find the right key
        rsa_key = {}
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
                break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")

        # Verify the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=settings.auth0_algorithms,
            audience=settings.auth0_audience,
            issuer=f'https://{settings.auth0_domain}/'
        )

        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from Auth0 token or local demo token."""
    return get_or_create_user_from_token(credentials.credentials, db)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from Auth0 token or local demo token, if present."""
    if not credentials:
        return None

    try:
        return get_or_create_user_from_token(credentials.credentials, db)
    except Exception:
        # Optional auth should not block anonymous OCR/formatting requests.
        return None
