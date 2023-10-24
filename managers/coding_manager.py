from flask import g
from sqlalchemy import select, func
from typing import List
from models.db_models import TestCase, Problem, Language


def find_test_cases(problem_id: int) -> List[TestCase]:
    q = select(TestCase).join(Problem).where(Problem.id == problem_id).order_by(func.random())
    return g.session.scalars(q).fetchall()


def find_problems(language_id: int) -> List[Problem]:
    q = select(Problem).join(Language).where(Language.id == language_id)
    return g.session.scalars(q).fetchall()
