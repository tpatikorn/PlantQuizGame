from flask import Blueprint, render_template, jsonify, send_from_directory

from managers.image_manager import fetch_tags, fetch_image_from_id

bp = Blueprint('main', __name__)

@bp.route('/index')
@bp.route('/')
def index():
    return render_template("index.html", types=fetch_tags())


# sanity check route
@bp.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@bp.get('/images/<image_id>')
def images(image_id):
    img = fetch_image_from_id(image_id)
    return send_from_directory(img.dir, img.filename)


@bp.get('/terms')
def terms():
    return render_template('terms.html')