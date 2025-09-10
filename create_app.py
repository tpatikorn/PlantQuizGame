from flask import Flask, render_template, jsonify, send_from_directory, url_for
from flask_cors import CORS
from flask_socketio import SocketIO

from managers.image_manager import fetch_tags, fetch_image_from_id

socketio = SocketIO()


def create_app(debug=False):
    # instantiate the app
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.debug = debug
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    CORS(app, resources={r'/*': {'origins': '*'}})  # enable CORS

    @app.route('/index')
    @app.route('/')
    def index():
        return render_template("index.html", types=fetch_tags())

    # sanity check route
    @app.route('/ping', methods=['GET'])
    def ping_pong():
        return jsonify('pong!')

    @app.get('/images/<image_id>')
    def images(image_id):
        img = fetch_image_from_id(image_id)
        return send_from_directory(img.dir, img.filename)

    @app.get('/terms')
    def terms():
        return render_template('terms.html')

    socketio.init_app(app)
    return app
