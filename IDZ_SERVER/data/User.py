import sqlalchemy
from .db_session import SqlAlchemyBase as db

class User(db):
    __tablename__ = 'user'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    secname = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    group = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
