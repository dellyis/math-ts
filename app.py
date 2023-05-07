import asyncio

from quart import Quart, render_template, request, session, redirect

from auth import auth_required, verify_auth
from blueprints import register_blueprints
from config import SECRET_KEY
from db import User, games, teams, users

app = Quart(__name__)
app.secret_key = SECRET_KEY

register_blueprints(app)


@app.before_serving
async def on_startup():
    await games.cache_all()


@app.before_request
async def make_session_permanent():
    session.permanent = True


@app.route("/")
async def index():
    await games.cache_all()
    await users.cache_all()
    await teams.cache_all()

    return await render_template("index.html")


@app.route("/rules")
async def rules():
    return await render_template("rules.html")


@app.route("/profile")
@auth_required(True)
async def profile(user: User):
    return await render_template(
        "profile.html",
        data={
            "name": user.name,
        },
    )


@app.route("/login")
async def login_page():
    if (await verify_auth(request))[0]:
        return redirect(request.args.get("redirect_uri", "/profile"))

    return await render_template("login.html", **dict(request.args))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app.run(host="0.0.0.0", debug=True, loop=loop)
