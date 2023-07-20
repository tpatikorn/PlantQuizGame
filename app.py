from flask import Flask, jsonify, send_file
from flask_cors import CORS
from waitress import serve
from connectors.db_connector import db


def create_app():
    # instantiate the app
    app = Flask(__name__)
    app.config.from_object(__name__)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # enable CORS
    CORS(app, resources={r'/*': {'origins': '*'}})
    app.teardown_appcontext(db.terminate)
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
