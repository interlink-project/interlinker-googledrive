from fastapi import Depends, HTTPException, Request
import jwt
from jwt import PyJWKClient

url = "https://aac.platform.smartcommunitylab.it/jwk"
jwks_client = PyJWKClient(url)

def decode_token(jwtoken):
    signing_key = jwks_client.get_signing_key_from_jwt(jwtoken)
    data = jwt.decode(
        jwtoken,
        signing_key.key,
        algorithms=["RS256"],
        audience="c_0e0822df-9df8-48d6-b4d9-c542a4623f1b",
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
        return request.headers.get('authorization').replace("Bearer ", "")
    except:
        return None


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