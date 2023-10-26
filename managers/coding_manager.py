from flask import g
from sqlalchemy import select, func
from typing import List
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


if __name__ == "__main__":
    def to_test():
        print(find_categories(language_id=1))
        print(find_problems(category_id=1))


    from util.simple_main_test import test_this

    test_this(to_test)
