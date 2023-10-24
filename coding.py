from flask import Blueprint, render_template, jsonify
from managers import coding_manager

bp = Blueprint('coding', __name__, url_prefix='/coding')


@bp.route('/code_runner')
def code_runner():
    problems = coding_manager.find_problems(language_id=1)
    return render_template("code_runner.html", problems=problems)


@bp.route('/code_test', methods=["POST"])
def code_test():
    from flask import request
    from managers.test_sandbox import SandboxPython
    body = request.get_json()
    code = body["code"]
    test_cases = coding_manager.find_test_cases(body["problem_id"])
    all_inputs = [[float(_) for _ in test_case.test_inputs.split(",")] for test_case in test_cases]
    all_outputs = [float(test_case.test_outputs) for test_case in test_cases]
    print(all_inputs, all_outputs)
    sb = SandboxPython()
    result = sb.run(code, all_inputs, all_outputs)
    print(code, result)
    return jsonify(result)
