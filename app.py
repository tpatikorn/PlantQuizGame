from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
from waitress import serve
from managers.image_manager import fetch_image_tags, fetch_image_from_id

import auth, game


def create_app():
    # instantiate the app
    app = Flask(__name__)
    app.config.from_object(__name__)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    @app.before_request
    def init(*args):
        auth.load_logged_in_user()
        pass

    @app.teardown_appcontext
    def teardown(*args):
        pass

    # enable CORS
    CORS(app, resources={r'/*': {'origins': '*'}})
    app.register_blueprint(auth.bp)
    app.register_blueprint(game.bp)

    @app.route('/index')
    @app.route('/')
    def index():
        return render_template("index.html", types=fetch_image_tags())

    # sanity check route
    @app.route('/ping', methods=['GET'])
    def ping_pong():
        return jsonify('pong!')

    @app.get('/images/<image_id>')
    def images(image_id):
        img = fetch_image_from_id(image_id)
        return send_from_directory(img.dir, img.filename)

    return app


serve(create_app(), host="0.0.0.0", port=8080)
