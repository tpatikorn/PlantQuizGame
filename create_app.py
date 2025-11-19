from flask import Flask, render_template, jsonify, send_from_directory, url_for
from flask_cors import CORS
from flask_socketio import SocketIO

from managers.image_manager import fetch_tags, fetch_image_from_id

socketio = SocketIO(cors_allowed_origins="*")
app = Flask(__name__)


def create_app(debug=False):
    # instantiate the app
    app.config.from_object(__name__)
    app.debug = debug
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    CORS(app, resources={r'/*': {'origins': '*'}})  # enable CORS

    # the true main page of everything
    @app.route('/')
    def index():
        return render_template("main.html")

    socketio.init_app(app)
    return app
