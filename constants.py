from enums import GameEnum

from config import PRODUCTION, DOMAIN


GAMES = {
    GameEnum.domino.value: ("domino", "Домино"),
    GameEnum.krestiki.value: ("krestiki", "Крестики-нолики"),
    GameEnum.bonus.value: ("bonus", "Бонусы"),
}

if PRODUCTION:
    HOST = f"https://{DOMAIN}"
else:
    HOST = "http://localhost:5000"
