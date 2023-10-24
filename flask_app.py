from html import escape

from flask import g
from flask_socketio import emit, join_room

from app import create_app, socketio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    # Connect to an existing database
    engine = create_engine("postgresql://%s:%s@%s:%s/%s" %
                           (os.getenv("DB_USER"),
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


    @socketio.on('chat')
    def chat(data):
        username = escape(data[0])
        message = escape(data[1])
        room = escape(data[2])
        emit('chat_response', [username, message, room], to=room)


    @socketio.on('join')
    def join(data):
        username = escape(data[0])
        room = escape(data[1])
        join_room(room)
        emit('join_response', ["SYSTEM", f"{username} has joined the room '{room}'", room], to=room)


    import auth
    import game
    import coding

    this_app.register_blueprint(auth.bp)
    this_app.register_blueprint(game.bp)
    this_app.register_blueprint(coding.bp)

    auth.oauth.init_app(this_app)

    socketio.run(this_app, "127.0.0.1", 8080)
