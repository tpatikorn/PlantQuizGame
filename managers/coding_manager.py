from flask import g, session
from sqlalchemy import select, func
from typing import List, Dict, Tuple

from sqlalchemy.dialects.postgresql import insert

from managers.test_sandbox import SandboxPython
from models.db_models import TestCase, Problem, Category, CodeSubmission


def find_test_cases(problem_id: int) -> List[TestCase]:
    q = select(TestCase).join(Problem).where(Problem.id == problem_id).order_by(func.random())
    return g.session.scalars(q).fetchall()


def find_categories(language_id: int) -> List[Problem]:
    q = select(Category).where(Category.language_id == language_id)
    return g.session.scalars(q).fetchall()


def find_problems(category_id: int) -> List[Problem]:
    q = select(Problem).where(Problem.category_id == category_id)
    return g.session.scalars(q).fetchall()


def create_test_case(problem_id: int, test_inputs: str, test_outputs: str, public: bool) -> TestCase:
    q = insert(TestCase).values(problem_id=problem_id, test_inputs=test_inputs,
                                test_outputs=test_outputs, public=public).returning(TestCase.id)
    result = g.session.execute(q)
    g.session.commit()
    return result.first()[0]


def create_problem(name: str, category_id: int, description_th: str, description_en: str,
                   input_format: str, output_format: str) -> int:
    q = insert(Problem).values(name=name, category_id=category_id,
                               description_th=description_th, description_en=description_en,
                               input_format=input_format, output_format=output_format).returning(Problem.id)
    result = g.session.execute(q)
    g.session.commit()
    return result.first()[0]


def test_code(code: str, problem_id: int = None, test_inputs: List[str] = None) \
        -> Tuple[List[Tuple[str, str, str]], int, int, int]:
    if problem_id:
        test_cases = find_test_cases(problem_id)
    else:
        problem_id = 0
        test_cases = [
            TestCase(id=0, problem_id=0, test_inputs=test_input, test_outputs=0, public=True, active=True, problem=None)
            for test_input in test_inputs]
    results = SandboxPython().run(code, test_cases, result_only=(problem_id == 0), verbose=False)
    q = insert(CodeSubmission).values(problem_id=problem_id, user_id=session['user']['id'], code=code,
                                      passed=results[1], failed=results[2], raised=results[3])
    g.session.execute(q)
    g.session.commit()
    return results


def submit_code(body: Dict):
    code = body["code"]
    if "problem_id" in body.keys():
        test_cases = find_test_cases(body["problem_id"])
    else:
        test_cases = [
            TestCase(id=0, problem_id=0, test_inputs=test_input, test_outputs=0, public=True, active=True, problem=None)
            for test_input in body["test_inputs"].split("\n")]
    sb = SandboxPython()
    return sb.run(code, test_cases, result_only=True, verbose=True)


if __name__ == "__main__":
    def to_test():
        print(find_categories(language_id=1))
        print(find_problems(category_id=1))
        print(create_problem("power of 2", 1, "return x raised to the power of 2", "return ค่่า x ยกกำลังสอง",
                             "x: float", "float"))


    from util.simple_main_test import test_this

    test_this(to_test)
