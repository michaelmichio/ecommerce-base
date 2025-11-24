from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings

ALGORITHM = "HS256"


def _sanitize_payload(data: dict) -> dict:
    """
    Ensures all values inside JWT payload are JSON-serializable.
    Converts UUID and other unsupported types into strings.
    """
    cleaned = {}

    for key, value in data.items():
        # Convert UUID or other non-serializable objects to strings
        if not isinstance(value, (str, int, float, bool, type(None))):
            cleaned[key] = str(value)
        else:
            cleaned[key] = value

    return cleaned


# =====================================================================
# 🔐 Create Access Token
# =====================================================================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = _sanitize_payload(data)

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES)
    )

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(
        to_encode,
        settings.ACCESS_SECRET,
        algorithm=ALGORITHM
    )


# =====================================================================
# 🔁 Create Refresh Token
# =====================================================================
def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = _sanitize_payload(data)

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_EXPIRE_DAYS)
    )

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(
        to_encode,
        settings.REFRESH_SECRET,
        algorithm=ALGORITHM
    )


# =====================================================================
# 🔍 Decode Access Token
# =====================================================================
def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.ACCESS_SECRET,
            algorithms=[ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


# =====================================================================
# 🔍 Decode Refresh Token
# =====================================================================
def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.REFRESH_SECRET,
            algorithms=[ALGORITHM]
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
