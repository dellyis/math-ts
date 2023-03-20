from flask import redirect, request

from db import session, User


def auth_required(get_account: bool = False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = request.cookies.get("access_token")

            if not token:
                return redirect(f"/login?redirect_uri={request.full_path}")

            account = session.query(User).filter_by(access_token=token).first()

            if not account:
                return redirect(f"/login?redirect_uri={request.full_path}")

            if get_account:
                return func(account=account, *args, **kwargs)

            return func(*args, **kwargs)

        setattr(wrapper, "__name__", func.__name__)

        return wrapper

    return decorator
