import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings

security = HTTPBasic()


def verify_password(credentials: HTTPBasicCredentials = Depends(security)) -> HTTPBasicCredentials:
    password_ok = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        settings.app_password.encode("utf-8"),
    )
    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials
