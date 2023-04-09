import secrets

from passlib.hash import sha256_crypt
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("sqlite:///data.db")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    login = Column(String, unique=True)
    email = Column(String)
    password_hash = Column(String(100), nullable=False)
    access_token = Column(String(32), unique=True, nullable=True)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "login": self.login,
            "email": self.email,
        }

    @password.setter
    def password(self, password):
        self.password_hash = sha256_crypt.hash(password)

    def verify_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)  # type: ignore

    def generate_access_token(self):
        self.access_token = secrets.token_hex(16)
        session.commit()


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
