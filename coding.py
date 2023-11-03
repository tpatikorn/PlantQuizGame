import json

from flask import Blueprint, render_template, jsonify, request, session

from auth import login_required
from managers import coding_manager
from managers.coding_manager import test_code
from models.db_models import TestCase

bp = Blueprint('coding', __name__, url_prefix='/coding')


@bp.route('/code_test_maker')
def code_test_maker():
    categories = coding_manager.find_categories(language_id=1)
    return render_template("code_test_maker.html", categories=categories)


@bp.route('/code_runner')
def code_runner():
    categories = coding_manager.find_categories(language_id=1)
    return render_template("code_runner.html", categories=categories)


@bp.route('/fetch_problems')
def fetch_problems():
    results = coding_manager.find_problems(category_id=int(request.args.get("category_id")))
    return [_.to_json() for _ in results]


@bp.route('/code_create_problem', methods=["POST"])
@login_required
def code_create_problem():
    if "user" not in session.keys():
        return "You cannot test code while not logged in.", 403
    from managers.test_sandbox import PythonSandbox
    body = request.get_json()
    new_problem_id = coding_manager.create_problem(name=body["name"],
                                                   category_id=body["category_id"],
                                                   description_en=body["description_en"],
                                                   description_th=body["description_th"],
                                                   input_format=body["input_format"],
                                                   output_format=body["output_format"])

    code = body["code"]
    test_cases = [
        TestCase(id=0, problem_id=0, test_inputs=test_input, test_outputs=0, public=True, active=True, problem=None)
        for test_input in body["test_inputs"].split("\n")]
    sb = PythonSandbox()
    results = sb.run(code, test_cases, result_only=True)
    for test_case in results[0]:
        coding_manager.create_test_case(problem_id=new_problem_id, test_inputs=test_case[0], test_outputs=test_case[2],
                                        public=True)
    return jsonify(results)


@bp.route('/code_test', methods=["POST"])
@login_required
def code_test():
    body = request.get_json()
    if "problem_id" in body.keys():
        return jsonify(test_code(body["code"],
                                 problem_id=body["problem_id"]))
    else:
        return jsonify(test_code(body["code"],
                                 test_inputs=body["test_inputs"],
                                 input_format=json.dumps(body["input_format"])))
