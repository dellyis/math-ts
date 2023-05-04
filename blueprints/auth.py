import re

from quart import Blueprint, make_response, redirect, request

from db import User, users
from snowflake import snowflake_generator

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


login_pattern = re.compile("^[a-z0-9_-]{3,16}$")
email_pattern = re.compile(
    """(?:[a-z0-9!#$%&'*+\=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""  # type: ignore
)
password_pattern = re.compile("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).{8,}$")  # type: ignore
bday_pattern = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")


@auth_bp.route("/login", methods=["POST"])
async def login():
    form = await request.form
    login = form.get("login")
    password = form.get("password")

    if not (login and password):
        return redirect("/login?login_err_not_filled")

    user = await users.find_by_field(login=login)

    if not user or not User.verify_password(password, user.password):
        return redirect("/login?login_err")

    async with user.command_maker() as edit_user:
        edit_user.access_token = User.generate_access_token()

    response = await make_response(redirect("/profile"))
    response.set_cookie("Authorization", user.access_token)
    return response


@auth_bp.route("/register", methods=["POST"])
async def register():
    form = await request.form
    name = form.get("name")
    login = form.get("login")
    email = form.get("email")
    bday = form.get("bday")
    password = form.get("password")
    confirm_password = form.get("confirm-password")

    if not (name and login and email and password and confirm_password and bday):
        return redirect("/login?reg_err_not_filled#reg")

    if not all(
        [
            login_pattern.match(login),
            email_pattern.match(email),
            password_pattern.match(password),
            bday_pattern.match(bday),
        ]
    ):
        return redirect("/login?reg_err_pattern#reg")

    if (await users.find_by_field(login=login)) or (
        await users.find_by_field(email=email)
    ):
        return redirect("/login?reg_err_used#reg")

    if password != confirm_password:
        return redirect("/login?reg_err_confirm#reg")

    user = await users.find(str(snowflake_generator.generate()))

    async with user.command_maker() as edit_user:
        edit_user.name = name
        edit_user.login = login
        edit_user.email = email
        edit_user.bday = User.format_bday(bday)
        edit_user.password = User.get_password_hash(password)
        edit_user.access_token = User.generate_access_token()

    response = await make_response(redirect("/profile"))
    response.set_cookie("Authorization", user.access_token)
    return response
