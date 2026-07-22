from slowapi import Limiter
from fastapi import Request
from jose import jwt, JWTError
from app.core.config import settings

def get_real_ip(request: Request) -> str:
    # Render appends the verified client IP to the right of X-Forwarded-For.
    # We must not trust the leftmost IP if a user spoofs it.
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        ips = [ip.strip() for ip in xff.split(",") if ip.strip()]
        if ips:
            return ips[-1]
    
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"

def custom_key_func(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except JWTError:
            # Token invalid/expired/tampered. Do NOT grant authenticated quota.
            pass
            
    # Anonymous fallback using spoof-resistant IP extraction
    return get_real_ip(request)

limiter = Limiter(key_func=custom_key_func)
