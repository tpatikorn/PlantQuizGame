from html import escape
from flask import g
from flask_socketio import emit
from app import create_app, socketio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    # Connect to an existing database
    engine = create_engine("postgresql://%s:%s@%s:5432/%s" %
                           (os.getenv("DB_USER"),
                            os.getenv("DB_PASS"),
                            os.getenv("DB_SERVER"),
                            os.getenv("DB_DB")))

    Session = sessionmaker(bind=engine)
    this_app = create_app(debug=True)


    @this_app.teardown_appcontext
    def teardown(*args):
        pass


    @this_app.before_request
    def init(*args):
        g.session = Session()
        auth.load_logged_in_user()


    @socketio.on('chat')
    def handle_my_custom_event(data):
        print(data[0], data[1])
        username = escape(data[0])
        message = escape(data[1])
        emit('chat_response', [username, message], broadcast=True)


    import auth
    import game

    this_app.register_blueprint(auth.bp)
    this_app.register_blueprint(game.bp)
    socketio.run(this_app, "127.0.0.1", 8080)