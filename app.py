from flask import abort, Flask, redirect, render_template, request, make_response

from auth import auth_required
from db import session, User

app = Flask(__name__)

results = [
    {"name": "Команда 1", "school": "Школа 1", "score": 0},
    {"name": "Команда 2", "school": "Школа 2", "score": 0},
    {"name": "Команда 3", "school": "Школа 3", "score": 0},
    {"name": "Команда 4", "school": "Школа 4", "score": 0},
    {"name": "Команда 5", "school": "Школа 5", "score": 0},
]


@app.errorhandler(403)
def not_enough_perms_err(err):
    return render_template(
        "error.html", description="Недостаточно прав для выполнения данного действия; "
                                  "Расскажите организатору о том, как вы сюда попали :)"
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/leaders")
def leaders():
    return render_template(
        "leaders.html",
        results=results,
        zip=zip,
    )


@app.route("/profile")
@auth_required(True)
def profile(account: User):
    return render_template(
        "profile.html",
        data={
            "name": account.name,
            "perms": account.perms,
            "orgs": list(
                map(lambda el: el.json, session.query(User).filter_by(perms=2).all())
            ),
        },
    )


@app.route("/add/org", methods=["POST"])
@auth_required(True)
def add_org(account: User):
    if account.perms != 3:
        return abort(403)
    if session.query(User).filter_by(login=request.form.get("login")).all():
        return abort(333)
    session.add(
        User(
            name=request.form.get("name"),
            login=request.form.get("login"),
            password=request.form.get("password"),
            perms=2,
        )
    )
    session.commit()
    return redirect("/profile")


@app.route("/delete/org/<int:user_id>")
@auth_required(True)
def delete_org(account: User, user_id: int):
    if account.perms != 3:
        return abort(406)
    data = session.query(User).filter_by(id=user_id).first()
    if data:
        session.delete(data)
        session.commit()
    return redirect("/profile")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        account = session.query(User).filter_by(login=login).first()
        if account and account.verify_password(password):
            account.generate_access_token()
            redirect_uri = request.args.get("redirect_uri", "/profile")
            response = make_response(redirect(redirect_uri))
            response.set_cookie("access_token", account.access_token, max_age=43200)  # type: ignore
            return response
        return render_template("login.html", error=True)
    else:
        return render_template("login.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
