from quart import redirect, request

from db import User, users


def auth_required(get_account: bool = False):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            token = request.cookies.get("Authorization")

            if not token:
                return redirect(f"/login?redirect_uri={request.full_path}")

            account = await users.find_by_field(access_token=token)

            if not account:
                return redirect(f"/login?redirect_uri={request.full_path}")

            if get_account:
                return await func(account=account, *args, **kwargs)

            return await func(*args, **kwargs)

        setattr(wrapper, "__name__", func.__name__)

        return wrapper

    return decorator
