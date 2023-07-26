import random

from flask import Flask, jsonify, send_file, make_response, url_for, render_template, g, request, Blueprint, \
    send_from_directory
from flask_cors import CORS
from waitress import serve

from controllers.quiz_controller import image_treasure_hunt, image_quick_draw
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
        auth.load_logged_in_user()
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
        n_pics = int(request.args.get("n_pics", default=25))
        n_correct = int(request.args.get("n_correct", default=5))
        n_col = int(request.args.get("n_col", default=5))
        target_type = request.args.get("target_type", default="durian")
        n_correct = min(n_correct, n_pics)

        if target_type == "random":
            category = random.sample(ImageCacheManager.get_image_categories(exclude_sub=True), 1)[0]
        else:
            category = list(filter(lambda _: _.name == target_type, ImageCacheManager.get_image_categories()))[0]
        img, ans = image_treasure_hunt(n_pics, n_correct, category.id)
        return render_template("treasure_hunt.html", img=img, ans=ans,
                               n_col=n_col, target_type=category.name, n_correct=n_correct)

    @app.route('/quick_draw', methods=['GET'])
    def quick_draw():
        ImageCacheManager.update_cache()
        n_rounds = int(request.args.get("n_rounds", default=10))
        n_choices = int(request.args.get("n_choices", default=2))
        n_choices = max(min(n_choices, 4), 2)
        target_type = request.args.get("target_type", default="durian")
        print(target_type)

        if target_type == "random":
            category = random.sample(ImageCacheManager.get_image_categories(exclude_sub=True), 1)[0]
        else:
            category = list(filter(lambda _: _.name == target_type, ImageCacheManager.get_image_categories()))[0]

        img, ans = image_quick_draw(n_rounds, n_choices, category.id)
        return render_template("quick_draw.html", img=img, ans=ans,
                               n_rounds=n_rounds, target_type=category.name, n_choices=n_choices)

    @app.get('/images/<image_id>')
    def images(image_id):
        img = ImageCacheManager.get_image(image_id)
        return send_from_directory(img.dir, img.filename)

    return app


serve(create_app(), host="0.0.0.0", port=8080)
