import secrets

from passlib.hash import sha256_crypt
from motor.motor_tornado import MotorClient

from config import MONGO_TOKEN
from db_core import NiceCollection, NiceDocument, field


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
    password: str = field()
    access_token: str = field()

    @staticmethod
    def generate_access_token():
        return secrets.token_hex(16)

    @staticmethod
    def get_password_hash(password: str):
        return sha256_crypt.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str):
        return sha256_crypt.verify(password, password_hash)


cluster = MotorClient(MONGO_TOKEN)
db = cluster["dev"]
users = FieldCollectionEngine(db["users"], User)
