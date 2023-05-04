import secrets
from datetime import datetime
from typing import Set

from motor.motor_tornado import MotorClient
from passlib.hash import sha256_crypt

from config import MONGO_TOKEN
from db_core import (
    NiceCollection,
    NiceDocument,
    NiceNesting,
    field,
    field_with_set,
    nesting,
)


class FieldCollectionEngine(NiceCollection):
    async def find_by_field(self, **fields):
        for doc in self.cache.values():
            if all(getattr(doc, field) == value for field, value in fields.items()):
                return doc
        data = await self.mongo_col.find_one(fields)
        if data is None:
            return None
        doc = self.document_wrapper(data, self)
        self.cache[doc.id] = doc
        return doc


class User(NiceDocument):
    name: str = field()
    login: str = field()
    email: str = field()
    teams: Set[str] = field_with_set()
    bday: datetime = field()
    password: str = field()
    access_token: str = field()

    @staticmethod
    def format_bday(date: str) -> datetime:
        return datetime.strptime(date, "%Y-%m-%d")

    @staticmethod
    def get_password_hash(password: str) -> str:
        return sha256_crypt.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return sha256_crypt.verify(password, password_hash)

    @staticmethod
    def generate_access_token() -> str:
        return secrets.token_hex(16)

    @staticmethod
    def get_age(bday: datetime) -> int:
        return (datetime.utcnow() - bday).days // 365


class Team(NiceDocument):
    name: str = field()
    owner: str = field()
    members: Set[str] = field_with_set()
    invite: str = field()

    @staticmethod
    def generate_invite() -> str:
        return secrets.token_hex(16)


class GameOrg(NiceNesting):
    name: str = field()
    short_name: str = field()
    site: str = field()
    icon: str = field()
    email: str = field()


class GameLimits(NiceNesting):
    age: Set[int] = field_with_set()
    team_size: int = field()


class Game(NiceDocument):
    game: int = field()
    start: int = field()
    duration: int = field()
    org: GameOrg = nesting(GameOrg)
    limits: GameLimits = nesting(GameLimits)
    teams: Set[str] = field_with_set()


cluster = MotorClient(MONGO_TOKEN)
db = cluster["dev"]
users = FieldCollectionEngine(db["users"], User)
games = FieldCollectionEngine(db["games"], Game)
teams = FieldCollectionEngine(db["teams"], Team)
