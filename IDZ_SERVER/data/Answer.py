import sqlalchemy
from .db_session import SqlAlchemyBase as db

class Answer(db):
    __tablename__ = 'answer'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    right = sqlalchemy.Column(sqlalchemy.Double, nullable=False)