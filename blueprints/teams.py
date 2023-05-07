from quart import Blueprint, redirect, render_template, request

from argsparser import ParsedArg, url_params
from auth import auth_required
from constants import HOST
from db import Team, User, teams, users
from snowflake import snowflake_generator

teams_bp = Blueprint("teams", __name__, url_prefix="/teams")


@teams_bp.route("/create", methods=["GET", "POST"])
@auth_required(True)
async def team_create_page(user: User):
    if request.method == "GET":
        return await render_template("team_create.html")

    form = await request.form
    name = form.get("name")

    if not name:
        return await render_template("team_create.html", err_not_filled=True)

    team = await teams.find(str(snowflake_generator.generate()))

    async with team.command_maker() as edit_team:
        edit_team.name = name[:64]
        edit_team.owner = user.id
        edit_team.members.add(user.id)
        edit_team.invite = Team.generate_invite()

    return redirect(f"/teams/{team.id}")


@teams_bp.route("/<team_id>")
@auth_required(True)
async def team_page(user: User, team_id: str):
    team = await teams.find(team_id)

    if user.id not in team.members:
        return await render_template(
            "error.html", description="Вы не участник этой команды"
        )

    team_members = [await users.find(member_id) for member_id in team.members]

    return await render_template(
        "team.html",
        team=team,
        team_members=team_members,
        user=user,
        host=HOST,
    )


@teams_bp.route("/<team_id>/kick/<member_id>")
@auth_required(True)
@url_params
async def kick_member(
    user: User, team_id: str, member_id: str, self: ParsedArg = "false"
):
    team = await teams.find(team_id)

    if user.id not in team.members:
        return await render_template(
            "error.html", description="Вы не участник этой команды"
        )

    if self not in ("true", "false"):
        return await render_template("error.html", description="incorr `self` param")

    self = self == "true"

    if (
        (self and user.id != member_id)
        or (not self and user.id == team.owner)
        or member_id == team.owner
    ):
        return await render_template("error.html", description="Недостаточно прав")

    if (not self and user.id == member_id) or member_id == team.owner:
        return await render_template(
            "error.html", description="Вы не можете себя выгнать из команды"
        )

    if self:
        async with team.command_maker() as edit_team:
            edit_team.members.remove(member_id)

        return redirect("/teams")

    async with team.command_maker() as edit_team:
        edit_team.members.remove(member_id)

    return redirect(f"/teams/{team_id}")


@teams_bp.route("/<team_id>/edit", methods=["GET", "POST"])
@auth_required(True)
async def team_edit_page(user: User, team_id: str):
    team = await teams.find(team_id)

    if user.id != team.owner:
        return await render_template("error.html", description="Недостаточно прав")

    if request.method == "GET":
        return await render_template("team_edit.html", team=team)

    form = await request.form
    name = form.get("name")

    if not name:
        return await render_template("team_edit.html", err_not_filled=True)

    async with team.command_maker() as edit_team:
        edit_team.name = name[:64]

    return redirect(f"/teams/{team_id}")


@teams_bp.route("/join/<team_invite>")
@auth_required(True)
async def join_team(user: User, team_invite: str):
    team = await teams.find_by_field(invite=team_invite)

    if not team:
        return await render_template("error.html", description="Приглашение не найдено")

    if user.id in team.members:
        return await render_template(
            "error.html", description="Вы уже вступили в эту команду"
        )

    async with team.command_maker() as edit_team:
        edit_team.members.add(user.id)

    return redirect(f"/teams/{team.id}")
