from time import time
from typing import Set

from quart import Blueprint, render_template

from auth import auth_required
from constants import GAMES
from db import Game, Team, User, games, teams, users
from utils import format_range, format_time

games_bp = Blueprint("games", __name__, url_prefix="/games")


@games_bp.route("/")
async def games_page():
    current_time = time()
    active_games = []
    future_games = []
    completed_games = []

    for game in games.cache.items():
        if game[1].start < current_time < game[1].start + game[1].duration:
            active_games.append(game)
        elif current_time < game[1].start:
            future_games.append(game)
        elif game[1].start + game[1].duration < current_time:
            completed_games.append(game)

    return await render_template(
        "games.html",
        active_games=sorted(active_games, key=lambda el: el[1].start),
        future_games=sorted(future_games, key=lambda el: el[1].start),
        completed_games=sorted(completed_games, key=lambda el: el[1].start),
        time_formatter=format_time,
        range_formatter=format_range,
        names=GAMES,
    )


@games_bp.route("/<game_id>")
async def game_page(game_id: str):
    game = await games.find(game_id)

    return await render_template(
        "game.html",
        game_id=game_id,
        game=game,
        names=GAMES,
        time_formatter=format_time,
        range_formatter=format_range,
    )


@games_bp.route("/<game_id>/request")
@auth_required(True)
async def game_request_page(user: User, game_id: str):
    game: Game = await games.find(game_id)

    user_teams: Set[Team] = set([await teams.find(team_id) for team_id in user.teams])

    for team in user_teams:
        team_ages = set(
            User.get_age((await users.find(member_id)).bday)
            for member_id in team.members
        )
        if (
            any(age not in game.limits.age for age in team_ages)
            or len(team.members) > game.limits.team_size
        ):
            user_teams.remove(team)

    return await render_template(
        "game_request.html",
        game_id=game_id,
        game=game,
        names=GAMES,
        user_teams=user_teams,
        user_age=User.get_age(user.bday),
    )
