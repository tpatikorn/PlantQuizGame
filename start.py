from flask_socketio import emit

from app import create_app, socketio

if __name__ == "__main__":
    this_app = create_app(debug=True)


    @this_app.teardown_appcontext
    def teardown(*args):
        pass


    @this_app.before_request
    def init(*args):
        auth.load_logged_in_user()


    @socketio.on('chat')
    def handle_my_custom_event(data):
        print(data)
        emit('chat_response', data, broadcast=True)


    import auth
    import game

    this_app.register_blueprint(auth.bp)
    this_app.register_blueprint(game.bp)
    socketio.run(this_app, "127.0.0.1", 8080)
