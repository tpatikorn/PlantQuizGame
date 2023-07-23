from flask import Flask, jsonify, send_file, make_response, url_for, render_template, g, request, Blueprint, \
    send_from_directory
from flask_cors import CORS
from waitress import serve

from controllers.quiz_controller import image_treasure_hunt
from managers.image_manager import ImageCacheManager


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
        return render_template("index.html")

    # sanity check route
    @app.route('/ping', methods=['GET'])
    def ping_pong():
        return jsonify('pong!')

    @app.route('/treasure_hunt', methods=['GET'])
    def treasure_hunt():
        ImageCacheManager.update_cache()
        durian = list(filter(lambda _: _.name == "durian", ImageCacheManager.get_image_categories()))[0]
        img, ans = image_treasure_hunt(25, 5, durian.id)
        return render_template("treasure_hunt.html", img=img, ans=ans, dim=5, zip=zip)

    @app.get('/images/<image_id>')
    def images(image_id):
        img = ImageCacheManager.get_image(image_id)
        return send_from_directory(img.dir, img.filename)

    return app


serve(create_app(), host="0.0.0.0", port=8080)
