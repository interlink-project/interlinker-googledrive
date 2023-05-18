from fastapi import Depends, HTTPException, Request
import jwt
from jwt import PyJWKClient
from app.config import settings
import os

url = "https://aac.platform.smartcommunitylab.it/jwk"
jwks_client = PyJWKClient(url)

def decode_token(jwtoken):
    signing_key = jwks_client.get_signing_key_from_jwt(jwtoken)
    data = jwt.decode(
        jwtoken,
        signing_key.key,
        algorithms=["RS256"],
        audience=os.getenv("CLIENT_ID"),
        # options={"verify_nbf": False},
    )
    return data

def get_token_in_cookie(request):
    try:
        return request.cookies.get("auth_token")
    except:
        return None


def get_token_in_header(request):
    try:
        return request.headers.get('Authorization').replace("Bearer ", "") 
    except:
        return None

async def check_origin_is_backend(request):
    try:
        token = get_token_in_header(request)
        if token != settings.BACKEND_SECRET:
            raise HTTPException(status_code=403)
        return
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=403)

def get_current_token(
    request: Request
) -> dict:
    return get_token_in_cookie(request) or get_token_in_header(request)


def get_current_active_token(
    current_token: str = Depends(get_current_token)
) -> dict:
    if not current_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return current_token


async def get_current_user_id(
    current_token: str = Depends(get_current_active_token)
):
    return decode_token(current_token).get("sub")