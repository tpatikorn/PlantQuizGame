from flask import Blueprint, request, render_template, session, redirect
from controllers.quiz_controller import image_treasure_hunt, image_quick_draw, image_chat
from managers.image_manager import fetch_tags
from models.db_models import Tag
from util.util import set_seed

bp = Blueprint('game', __name__, url_prefix='/game')


@bp.route('/treasure_hunt', methods=['GET'])
def treasure_hunt():
    n_pics = int(request.args.get("n_pics", default=25))
    n_correct = int(request.args.get("n_correct", default=5))
    n_cols = int(request.args.get("n_cols", default=5))
    target_type = request.args.get("target_type", default="durian")
    n_correct = min(n_correct, n_pics)
    seed = request.args.get("seed", default=set_seed())

    if target_type == "random":
        category = fetch_tags(limit=1, seed=seed)[0]
    else:
        category = fetch_tags(conditions=[Tag.name == target_type], limit=1)[0]
    img, ans = image_treasure_hunt(n_pics, n_correct, category.id, seed=seed)
    all_img_src = [f"/images/{i.id}" for i in img]

    obj = {
        "n_pics": n_pics,
        "n_correct": n_correct,
        "n_cols": n_cols,
        "target_type": target_type,
        "category": category.id,
        "img0": img[0].id,
        "ans0": ans[0],
        "img1": img[1].id,
        "ans1": ans[1],
        "img2": img[2].id,
        "ans2": ans[2]
    }
    print(obj)

    return render_template("treasure_hunt.html", img=img, ans=ans, all_img_src=all_img_src,
                           n_cols=n_cols, target_type=category.name, n_correct=n_correct)


@bp.route('/quick_draw', methods=['GET'])
def quick_draw():
    n_rounds = int(request.args.get("n_rounds", default=10))
    n_choices = int(request.args.get("n_choices", default=2))
    n_choices = max(min(n_choices, 9), 2)
    target_type_name = request.args.get("target_type", default="durian")
    seed = request.args.get("seed", default=set_seed())

    if target_type_name == "random":
        target_type = fetch_tags(limit=1, seed=seed)[0]
    else:
        target_type = fetch_tags(conditions=[Tag.name == target_type_name])[0]

    img, ans = image_quick_draw(n_rounds, n_choices, target_type.id, seed=seed)
    all_img_src = [f"/images/{i.id}" for i_row in img for i in i_row]
    return render_template("quick_draw.html", img=img, ans=ans, all_img_src=all_img_src,
                           n_rounds=n_rounds, target_type=target_type.name, n_choices=n_choices)


@bp.route('/chat', methods=['GET'])
def chat():
    try:
        session['user']
    except KeyError:
        return redirect("/")
    n_rounds = int(request.args.get("n_rounds", default=10))
    n_choices = int(request.args.get("n_choices", default=2))
    n_choices = max(min(n_choices, 9), 2)
    seed = request.args.get("seed", default=set_seed())

    img, ans = image_chat(n_rounds, n_choices, seed=seed)
    all_img_src = [f"/images/{i.id}" for i_row in img for i in i_row]

    return render_template("chat.html", img=img, ans=ans, all_img_src=all_img_src,
                           n_rounds=n_rounds, n_choices=n_choices)
