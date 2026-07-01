import base64
import json
import logging

logger = logging.getLogger(__name__)

def extract_user_id_from_jwt(token: str) -> str | None:
    """
    Decodes the JWT payload (no signature verification) and extracts the user GUID.
    Tries all claim names used by ASP.NET Identity / IdentityServer.
    """
    try:
        # Check if it's prefixed with Bearer
        token = token.strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        parts = token.split('.')
        if len(parts) != 3:
            return None
        # Base64url decode with padding fix
        payload_b64 = parts[1]
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        # urlsafe_b64decode converts - to + and _ to /
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # Try all known .NET JWT claim names in priority order
        candidates = [
            'nameid',
            'sub',
            'nameidentifier',
            'userId',
            'UserId',
            'id',
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier',
        ]
        for claim in candidates:
            val = payload.get(claim)
            if val and isinstance(val, str) and len(val) > 10:
                logger.info(f"[JWT] Extracted user_id from claim '{claim}': {val!r}")
                print(f"[JWT] Extracted user_id from claim '{claim}': {val!r}")
                return val
        
        logger.warning(f"[JWT] No user_id found. Payload keys: {list(payload.keys())}")
        print(f"[JWT] ⚠️ No user_id found in JWT. Keys: {list(payload.keys())}")
        return None
    except Exception as e:
        logger.error(f"[JWT] Failed to decode token: {e}")
        print(f"[JWT] ❌ Decode error: {e}")
        return None
