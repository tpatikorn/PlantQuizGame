import json

from flask import Blueprint, render_template, jsonify, request, session

from auth import login_required
from managers import coding_manager
from managers.coding_manager import test_code, eval_code
from models.db_models import TestCase, Problem

bp = Blueprint('coding', __name__)


@bp.route('/test_creator')
def test_creator():
    categories = coding_manager.find_categories(language_id=1)
    return render_template("test_creator.html", categories=categories)

@bp.route('/')
@bp.route('/test_runner')
def test_runner():
    categories = coding_manager.find_categories(language_id=1)
    return render_template("test_runner.html", categories=categories)


@bp.route('/fetch_problems')
def fetch_problems():
    results = coding_manager.find_problems(category_id=int(request.args.get("category_id")))
    return [_.to_json() for _ in results]


@bp.route('/fetch_best_score')
def fetch_best_score():
    if "user" in session.keys():
        result = coding_manager.find_best_score(problem_id=int(request.args.get("problem_id")))
    else:
        result = 0
    return jsonify(result)


@bp.route('/create_problem', methods=["POST"])
@login_required
def create_problem():
    body = request.get_json()
    results = eval_code(body["code"],
                        test_inputs=body["test_inputs"],
                        input_format=json.dumps(body["input_format"]))

    if results[2] + results[3] > 0:
        return "Cannot create a problem with erroneous results", 403

    new_problem_id = coding_manager.create_problem(name=body["name"],
                                                   category_id=body["category_id"],
                                                   description_en=body["description_en"],
                                                   description_th=body["description_th"],
                                                   input_format=json.dumps(body["input_format"]),
                                                   output_format=json.dumps(body["output_format"]))

    for test_case, is_public in zip(results[0], body["public_flags"]):
        coding_manager.create_test_case(problem_id=new_problem_id,
                                        test_inputs=test_case[0],
                                        test_outputs=test_case[2],
                                        public=is_public)
    return jsonify(results)


@bp.route('/test_problem', methods=["POST"])
@login_required
def test_problem():
    body = request.get_json()
    if "problem_id" in body.keys():
        return jsonify(test_code(body["code"],
                                 problem_id=body["problem_id"]))
    else:
        return jsonify(eval_code(body["code"],
                                 test_inputs=body["test_inputs"],
                                 input_format=json.dumps(body["input_format"])))
