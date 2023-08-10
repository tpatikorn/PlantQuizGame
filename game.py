from app import socketio
from flask import Blueprint, request, render_template
import random
from controllers.quiz_controller import image_treasure_hunt, image_quick_draw
from managers.image_manager import fetch_image_tags

bp = Blueprint('game', __name__, url_prefix='/game')


@bp.route('/treasure_hunt', methods=['GET'])
def treasure_hunt():
    n_pics = int(request.args.get("n_pics", default=25))
    n_correct = int(request.args.get("n_correct", default=5))
    n_cols = int(request.args.get("n_col", default=5))
    target_type = request.args.get("target_type", default="durian")
    n_correct = min(n_correct, n_pics)

    if target_type == "random":
        category = random.sample(fetch_image_tags(), 1)[0]
    else:
        category = list(filter(lambda _: _.name == target_type, fetch_image_tags()))[0]
    img, treasure_cat_id = image_treasure_hunt(n_pics, n_correct, category.id)
    all_img_src = [f"/images/{i.id}" for i in img]
    return render_template("treasure_hunt.html", img=img, treasure_cat_id=treasure_cat_id, all_img_src=all_img_src,
                           n_cols=n_cols, target_type=category.name, n_correct=n_correct)


@bp.route('/quick_draw', methods=['GET'])
def quick_draw():
    n_rounds = int(request.args.get("n_rounds", default=10))
    n_choices = int(request.args.get("n_choices", default=2))
    n_choices = max(min(n_choices, 9), 2)
    target_type_name = request.args.get("target_type", default="durian")

    if target_type_name == "random":
        target_type = random.sample(fetch_image_tags(), 1)[0]
    else:
        target_type = list(filter(lambda _: _.name == target_type_name, fetch_image_tags()))[0]

    img, correct_type_id = image_quick_draw(n_rounds, n_choices, target_type.id)
    all_img_src = [f"/images/{i.id}" for i_row in img for i in i_row]
    return render_template("quick_draw.html", img=img, correct_type_id=correct_type_id, all_img_src=all_img_src,
                           n_rounds=n_rounds, target_type=target_type.name, n_choices=n_choices)


@bp.route('/chat', methods=['GET'])
def chat():
    n_rounds = int(request.args.get("n_rounds", default=10))
    n_choices = int(request.args.get("n_choices", default=2))
    n_choices = max(min(n_choices, 9), 2)

    target_type = random.sample(fetch_image_tags(), n_rounds)[0]  # fixz`

    img, correct_type_id = image_quick_draw(n_rounds, n_choices, target_type.id)
    all_img_src = [f"/images/{i.id}" for i_row in img for i in i_row]
    correct_choices = [[1 if correct_type_id in i.tag_id else 0 for i in i_row] for i_row in img]
    print(correct_choices)
    return render_template("chat.html", img=img, correct_choices=correct_choices, all_img_src=all_img_src,
                           n_rounds=n_rounds, target_type=target_type.name, n_choices=n_choices)
