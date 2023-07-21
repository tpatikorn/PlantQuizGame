from flask import Flask, jsonify, send_file
from flask_cors import CORS
from waitress import serve


def create_app():
    # instantiate the app
    app = Flask(__name__)
    app.config.from_object(__name__)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    @app.before_request
    def init(*args):
        pass

    @app.teardown_appcontext
    def teardown(*args):
        pass

    # enable CORS
    CORS(app, resources={r'/*': {'origins': '*'}})
    import auth
    app.register_blueprint(auth.bp)

    @app.route('/')
    def hello_world():  # put application's code here
        print("?")
        return 'Hello Worldx!'

    @app.route('/index')
    def index():
        return send_file("templates/index.html")

    # sanity check route
    @app.route('/ping', methods=['GET'])
    def ping_pong():
        return jsonify('pong!')

    return app


serve(create_app(), host="0.0.0.0", port=8080)
