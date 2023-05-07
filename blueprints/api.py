from typing import Any, Dict

from quart import Blueprint, jsonify

from auth import api_auth_required
from db import User, users, teams, Team
from snowflake import snowflake_generator

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/teams/<team_id>", methods=["GET"])
@api_auth_required(True)
async def team_page(user: User, team_id: str):
    team: Team = await teams.find(team_id)
    team_response: Dict[str, Any] = team.json

    if user.id != team.owner:
        team_response.pop("invite")

    if user.id not in team.members:
        team_response.pop("members")
        team_response.pop("owner")

    return jsonify(team_response)
