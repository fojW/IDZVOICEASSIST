from flask import Flask, request, jsonify, make_response
from data import db_session
from data.User import User
from data.Question import Question
from data.Answer import Answer
from sqlalchemy import func
from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import exc as orm_exc
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init("db/base.sqlite")

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    secname = data['secname']
    group = data['group']

    db_sess = db_session.create_session()
    existing_user = db_sess.query(User).filter(User.name == name, User.secname == secname, User.group == group).first()
    if existing_user:
        return make_response(jsonify({'error': 'Такой пользователь уже существует'}), 400)

    user = User(name=name, secname=secname, group=group)

    db_sess.add(user)
    try:
        db_sess.commit()
    except:
        db_sess.rollback()
        return make_response(jsonify({'error': 'Ошибка в процессе регистрации'}), 500)

    return jsonify({'id': user.id}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data['name']
    secname = data['secname']
    group = data['group']

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == name, User.secname == secname, User.group == group).first()
    if user:
        return jsonify({'id':user.id}), 200
    else:
        return make_response(jsonify({'error': 'Неверные данные аутентификации'}), 401)

@app.route('/new_questions', methods=['POST'])
def new_questions():
    data = request.get_json()
    db_sess = db_session.create_session()

    db_sess.query(Question).delete()

    for question_data in data:
        text = question_data['text']
        answers = question_data['answers']
        right_answer = question_data['right_answer']

        question = Question(text=text, answers=answers, right_answer=right_answer)
        db_sess.add(question)

    db_sess.commit()

    return jsonify({'message': 'Вопросы добавлены успешно'}), 200

@app.route('/update_questions', methods=['POST'])
def update_questions():
    data = request.get_json()
    db_sess = db_session.create_session()

    for question_data in data:
        text = question_data['text']
        answers = question_data['answers']
        right_answer = question_data['right_answer']

        existing_question = db_sess.query(Question).filter(Question.text == text).first()
        if existing_question:
            existing_question.answers = answers
            existing_question.right_answer = right_answer
        else:
            question = Question(text=text, answers=answers, right_answer=right_answer)
            db_sess.add(question)

    db_sess.commit()

    return jsonify({'message': 'Вопросы обновлены успешно'}), 200

@app.route('/get_questions', methods=['GET'])
def get_questions():
    db_sess = db_session.create_session()

    questions = db_sess.query(Question).all()
    question_list = []

    for question in questions:
        question_data = {
            'id': question.id,
            'text': question.text,
            'answer': question.answers,
            #'right_answer': question.right_answer
        }
        question_list.append(question_data)

    return jsonify(question_list), 200

@app.route('/write_answers', methods=['POST'])
def write_answers():
    data = request.get_json()
    db_sess = db_session.create_session()

    user_id = data[0]
    results = [None]
    total_questions = 0
    correct_answers = 0

    for answer_data in data[1:]:
        question_id = int(list(answer_data.keys())[0])
        user_answer = sorted(list(answer_data.values())[0].split('#@'))

        question = db_sess.query(Question).get(question_id)
        if question is None:
            results.append({question_id: False})
            continue

        total_questions += 1
        correct_answer = sorted(question.right_answer.split('#@'))

        is_correct = user_answer == correct_answer
        results.append({question_id: is_correct})
        if is_correct:
            correct_answers += 1

    if total_questions > 0:
        percentage = (correct_answers * 100) / total_questions
        results[0] = round(percentage,2)
    else: results[0] = 0

    answer = Answer(user_id=user_id, right=results[0])
    try:
        db_sess.add(answer)
        db_sess.commit()
    except (exc.OperationalError, orm_exc.FlushError, SQLAlchemyError) as e:
        db_sess.rollback()
        time.sleep(1)  # Добавляем задержку в 1 секунду перед повторной попыткой
        try:
            db_sess.add(answer)
            db_sess.commit()
        except (exc.OperationalError, orm_exc.FlushError, SQLAlchemyError) as e:
            db_sess.rollback()
            return jsonify({'error': 'Ошибка записи в базу данных'}), 500
    return jsonify(results), 200

@app.route('/group_statistics', methods=['GET'])
def group_statistics():
    db_sess = db_session.create_session()

    group_name = request.args.get('group')

    query = db_sess.query(User.name, User.secname, Answer.right)\
        .join(Answer, User.id == Answer.user_id)\
        .filter(User.group == group_name)\
        .all()

    statistics = []

    for name, secname, right in query:
        statistics.append({
            'name': name,
            'secname': secname,
            'right': right
        })

    return jsonify(statistics), 200


@app.route('/total_statistics', methods=['GET'])
def total_statistics():
    db_sess = db_session.create_session()
    result = db_sess.query(User.group, func.avg(Answer.right).label('average_right')).join(Answer, User.id == Answer.user_id).group_by(User.group).all()

    group_stats = []
    for group, avg_r in result:
        group_stats.append({group: avg_r})

    return jsonify(group_stats), 200

if __name__ == '__main__':
    app.run(port=8080, host='26.139.60.34',debug=True, threaded=True)
