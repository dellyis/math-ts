from quart import make_response, redirect, request

from db import users


def auth_required(get_account: bool = False):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            token = request.cookies.get("Authorization")

            if not token:
                return redirect(f"/login?redirect_uri={request.full_path}")

            account = await users.find_by_field(access_token=token)

            if not account:
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
