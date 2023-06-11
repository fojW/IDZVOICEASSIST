from flask import Flask
from data import db_session
from data.User import User
from data.Question import Question
from data.Answer import Answer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

def main():
    db_session.global_init("db/base.sqlite")
    db_sess = db_session.create_session()
    app.run(debug=True)

if __name__ == '__main__':
    main()