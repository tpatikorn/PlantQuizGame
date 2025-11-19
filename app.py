from html import escape

from flask import g, jsonify
from flask_socketio import emit, join_room

import main
import poll
from create_app import create_app, socketio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from managers import poll_manager, user_manager

load_dotenv()
# Connect to an existing database
engine = create_engine(
    "postgresql://%s:%s@%s:%s/%s" % (os.getenv("DB_USER"),
                                     os.getenv("DB_PASS"),
                                     os.getenv("DB_SERVER"),
                                     os.getenv("DB_PORT"),
                                     os.getenv("DB_DB")))

Session = sessionmaker(bind=engine)
this_app = create_app(debug=True)


@this_app.teardown_appcontext
def teardown(*args):
    if hasattr(g, "session"):
        g.session.close()


@this_app.before_request
def init(*args):
    g.session = Session()


@socketio.on('chat', namespace="/PlantQuizGame")
def chat(data):
    username = escape(data[0])
    message = escape(data[1])
    room = escape(data[2])
    emit('chat_response', [username, message, room], to=room, namespace="/PlantQuizGame")


@socketio.on('join', namespace="/PlantQuizGame")
def join(data):
    username = escape(data[0])
    room = escape(data[1])
    join_room(room)
    emit('join_response', ["SYSTEM", f"{username} has joined the room '{room}'", room], to=room, namespace="/PlantQuizGame")


@socketio.on("poll_join_event", namespace="/PlantQuizGame")
def poll_join(data):
    # data is username, room
    g.session = Session()
    user_id = data[0]
    room_code: str = escape(data[1])
    join_room(room_code)
    user = user_manager.find_user_with_id(user_id)
    if user is not None:
        print("joining", user.email, room_code)
    emit('poll_join', [user_id], to=room_code, namespace="/PlantQuizGame")
    g.session.close()
    return room_code


@socketio.on("poll_open_question_event", namespace="/PlantQuizGame")
def poll_open_question_event(data):
    g.session = Session()
    # data is room, question text, CSV of choice text
    room_code: str = escape(data[0])
    question = escape(data[1])
    choices = data[2]
    new_q, new_ch = poll_manager.create_question(room_code, question, choices)
    emit('poll_open_question', [new_q, new_ch], to=room_code, namespace="/PlantQuizGame")
    g.session.close()


@socketio.on("poll_close_question_event", namespace="/PlantQuizGame")
def poll_close_question_event(data):
    print("poll_close_question_event", data[0])
    # data is room, question_id
    room = escape(data[0])
    emit('poll_close_question', data, to=room, namespace="/PlantQuizGame")


@socketio.on("poll_post_answer_event", namespace="/PlantQuizGame")
def poll_post_answer_event(data):
    print("poll_post_answer_event", data)
    g.session = Session()
    # data is room, user_id, answer_id
    room = escape(data[0])
    poll_manager.log_answer(user_id=data[1], answer_id=data[2])
    emit('poll_post_answer', data, to=room, namespace="/PlantQuizGame")
    print("room", data[1], data[2])
    g.session.close()


import auth
import game
import coding

this_app.register_blueprint(main.bp, url_prefix="/PlantQuizGame")
this_app.register_blueprint(auth.bp, url_prefix="/PlantQuizGame/auth")
this_app.register_blueprint(game.bp, url_prefix="/PlantQuizGame/game")
this_app.register_blueprint(poll.bp, url_prefix="/PlantQuizGame/poll")

# prepare to separate this
this_app.register_blueprint(coding.bp, url_prefix="/coding")

auth.oauth.init_app(this_app)

if __name__ == "__main__":
    socketio.run(this_app, "127.0.0.1", 18080, allow_unsafe_werkzeug=True)
