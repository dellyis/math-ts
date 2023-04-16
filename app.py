import asyncio
import re

from quart import Quart, make_response, redirect, render_template, request, session

from auth import auth_required
from config import SECRET_KEY
from db import User, users
from showflake import SnowflakeGenerator

app = Quart(__name__)
app.secret_key = SECRET_KEY

snowflake_generator = SnowflakeGenerator()

login_pattern = re.compile("^[a-z0-9_-]{3,16}$")
email_pattern = re.compile(
    """(?:[a-z0-9!#$%&'*+\=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""  # type: ignore
)
password_pattern = re.compile("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).{8,}$")  # type: ignore

results = [
    {"name": "Команда 1", "school": "Школа 1", "score": 0},
    {"name": "Команда 2", "school": "Школа 2", "score": 0},
    {"name": "Команда 3", "school": "Школа 3", "score": 0},
    {"name": "Команда 4", "school": "Школа 4", "score": 0},
    {"name": "Команда 5", "school": "Школа 5", "score": 0},
]


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route("/")
async def index():
    return await render_template("index.html")


@app.route("/rules")
async def rules():
    return await render_template("rules.html")


@app.route("/leaders")
async def leaders():
    return await render_template(
        "leaders.html",
        results=results,
        zip=zip,
    )


@app.route("/profile")
@auth_required(True)
async def profile(account: User):
    return await render_template(
        "profile.html",
        data={
            "name": account.name,
        },
    )


@app.route("/login", methods=["GET"])
async def login_page():
    return await render_template("login.html", **dict(request.args))


@app.route("/auth/login", methods=["POST"])
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


@app.route("/auth/register", methods=["POST"])
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

    user = await users.find(snowflake_generator.generate())

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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app.run(host="0.0.0.0", debug=True, loop=loop)
