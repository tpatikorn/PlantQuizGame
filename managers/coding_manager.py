from flask import g
from sqlalchemy import select, func
from typing import List

from sqlalchemy.dialects.postgresql import insert

from models.db_models import TestCase, Problem, Category


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


if __name__ == "__main__":
    def to_test():
        print(find_categories(language_id=1))
        print(find_problems(category_id=1))
        print(create_problem("power of 2", 1, "return x raised to the power of 2", "return ค่่า x ยกกำลังสอง",
                             "x: float", "float"))


    from util.simple_main_test import test_this

    test_this(to_test)
