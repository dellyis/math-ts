import secrets
from datetime import datetime
from typing import Dict, Set

from motor.motor_tornado import MotorClient
from passlib.hash import sha256_crypt

from config import MONGO_TOKEN
from db_core import (
    NiceCollection,
    NiceDocument,
    NiceNesting,
    field,
    field_with_set,
    field_with_nestings,
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

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "login": self.login,
            "email": self.email,
            "teams": list(self.teams),
            "bday": self.bday,
            "password": self.password,
            "access_token": self.access_token,
        }

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

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner,
            "members": list(self.members),
            "invite": self.invite,
        }

    @staticmethod
    def generate_invite() -> str:
        return secrets.token_hex(16)


class GameOrg(NiceNesting):
    name: str = field()
    short_name: str = field()
    site: str = field()
    icon: str = field()

    @property
    def json(self):
        return {
            "name": self.name,
            "short_name": self.short_name,
            "site": self.site,
            "icon": self.icon,
        }


class GameLimits(NiceNesting):
    age: Set[int] = field_with_set()
    team_size: int = field()

    @property
    def json(self):
        return {
            "age": list(self.age),
            "team_size": self.team_size,
        }


class GameTask(NiceNesting):
    number: str = field()
    title: str = field()
    description: str = field()
    answer: str = field()

    @property
    def json(self):
        return {
            "number": self.number,
            "title": self.title,
            "description": self.description,
            "answer": self.answer,
        }


class Game(NiceDocument):
    game: int = field()
    start: int = field()
    duration: int = field()
    org: GameOrg = nesting(GameOrg)
    limits: GameLimits = nesting(GameLimits)
    teams: Set[str] = field_with_set()
    tasks: Dict[int, GameTask] = field_with_nestings(GameTask)

    @property
    def json(self):
        return {
            "id": self.id,
            "game": self.game,
            "start": self.start,
            "duration": self.duration,
            "org": self.org,
            "limits": self.limits,
            "teams": list(self.teams),
            "tasks": self.tasks,
        }


cluster = MotorClient(MONGO_TOKEN)
db = cluster["dev"]
users = FieldCollectionEngine(db["users"], User)
games = FieldCollectionEngine(db["games"], Game)
teams = FieldCollectionEngine(db["teams"], Team)
