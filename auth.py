from typing import Optional, Tuple

from quart import make_response, redirect, request, Request, jsonify

from db import users, User


API_RESPONSE_403 = {
    "error": "Forbidden",
    "error_description": "You are not authorized to access this resource",
    "status": 403,
}


async def verify_auth(req: Request) -> Tuple[bool, Optional[User]]:
    token = req.cookies.get("Authorization")

    if not token:
        return False, None

    account = await users.find_by_field(access_token=token)

    if not account:
        return False, None

    return True, account


def auth_required(get_account: bool = False):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            status, account = await verify_auth(request)

            if not status:
                response = await make_response(
                    redirect(f"/login?redirect_uri={request.full_path}")
                )
                response.delete_cookie("Authorization")
                return response

            if get_account:
                return await func(user=account, *args, **kwargs)

            return await func(*args, **kwargs)

        setattr(wrapper, "__name__", func.__name__)

        return wrapper

    return decorator


def api_auth_required(get_account: bool = False):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            status, account = await verify_auth(request)

            if not status:
                response = await make_response(jsonify(API_RESPONSE_403))
                response.delete_cookie("Authorization")
                return response

            if get_account:
                return await func(user=account, *args, **kwargs)

            return await func(*args, **kwargs)

        setattr(wrapper, "__name__", func.__name__)

        return wrapper

    return decorator
