from .auth import *
from .games import *
from .teams import *


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(teams_bp)
