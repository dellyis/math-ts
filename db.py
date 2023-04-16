import secrets
from datetime import datetime
from typing import Set

from passlib.hash import sha256_crypt
from motor.motor_tornado import MotorClient

from config import MONGO_TOKEN
from db_core import NiceCollection, NiceDocument, field, field_with_set


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


class Game(NiceDocument):
    game: int = field()
    start: int = field()
    duration: int = field()
    org: str = field()
    limits: Set[int] = field_with_set()
    teams: Set[int] = field_with_set()


cluster = MotorClient(MONGO_TOKEN)
db = cluster["dev"]
users = FieldCollectionEngine(db["users"], User)
games = FieldCollectionEngine(db["games"], Game)
