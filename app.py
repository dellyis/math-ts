import asyncio

from quart import Quart, render_template, request, session

from auth import auth_required
from blueprints import register_blueprints
from config import SECRET_KEY
from db import User, games, teams, users

app = Quart(__name__)
app.secret_key = SECRET_KEY

register_blueprints(app)

results = [
    {"name": "Команда 1", "school": "Школа 1", "score": 0},
    {"name": "Команда 2", "school": "Школа 2", "score": 0},
    {"name": "Команда 3", "school": "Школа 3", "score": 0},
    {"name": "Команда 4", "school": "Школа 4", "score": 0},
    {"name": "Команда 5", "school": "Школа 5", "score": 0},
]


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


@app.route("/leaders")
async def leaders():
    return await render_template(
        "leaders.html",
        results=results,
        zip=zip,
    )


@app.route("/profile")
@auth_required(True)
async def profile(user: User):
    return await render_template(
        "profile.html",
        data={
            "name": user.name,
        },
    )


@app.route("/login", methods=["GET"])
async def login_page():
    return await render_template("login.html", **dict(request.args))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app.run(host="0.0.0.0", debug=True, loop=loop)
