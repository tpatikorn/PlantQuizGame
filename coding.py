from flask import Blueprint, render_template, jsonify, request
from managers import coding_manager

bp = Blueprint('coding', __name__, url_prefix='/coding')


@bp.route('/code_runner')
def code_runner():
    categories = coding_manager.find_categories(language_id=1)
    return render_template("code_runner.html", categories=categories)


@bp.route('/fetch_problems')
def fetch_problems():
    results = coding_manager.find_problems(category_id=int(request.args.get("category_id")))
    print(request.args.get("category_id"), results)
    return [_.to_json() for _ in results]


@bp.route('/code_test', methods=["POST"])
def code_test():
    from flask import request
    from managers.test_sandbox import SandboxPython
    body = request.get_json()
    code = body["code"]
    test_cases = coding_manager.find_test_cases(body["problem_id"])
    print(test_cases)
    sb = SandboxPython()
    result = sb.run(code, test_cases, verbose=True)
    return jsonify(result)
