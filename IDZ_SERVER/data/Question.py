import sqlalchemy
from .db_session import SqlAlchemyBase as db

class Question(db):
    __tablename__ = 'question'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    answers = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    right_answer = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)