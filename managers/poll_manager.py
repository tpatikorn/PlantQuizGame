import random
from typing import List, Tuple

from flask import g
from sqlalchemy import select, insert

from managers import user_manager
from models.db_models import PollRoom, PollQuestion, PollChoice, PollAnswer

CODE_LENGTH = 6
CODE_GEN_ATTEMPT = 10


def generate_code(k=CODE_LENGTH):
    characters = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    attempt_count = 0
    while True:
        # try until you find a valid key
        code = ''.join(random.choices(characters, k=k))
        try:
            find_room(room_code=code)
        except KeyError:
            return code
        # if it goes for too long and they're all dupes, increase the length
        if attempt_count >= CODE_GEN_ATTEMPT:
            k += 1
            attempt_count = 0


def create_room(name: str) -> PollRoom:
    code = generate_code()
    q = insert(PollRoom).values(name=name, code=code, user_id=user_manager.find_current_user_id()).returning(
        PollRoom.id)
    result = g.session.execute(q)
    print("session", g.session)
    g.session.commit()
    new_id = result.fetchall()[0][0]
    return find_room(room_id=new_id)


def find_room(room_id: int = None, room_code: str = None) -> PollRoom:
    if room_id is not None:
        try:
            print("session", g)
            q = select(PollRoom).where(PollRoom.id == room_id).where(PollRoom.active)
            return g.session.scalars(q).fetchall()[0]
        except IndexError:
            raise KeyError(f"cannot find room with id {room_id}")
    elif room_code is not None:
        try:
            print("session", g)
            q = select(PollRoom).where(PollRoom.code == room_code).where(PollRoom.active)
            return g.session.scalars(q).fetchall()[0]
        except IndexError:
            raise KeyError(f"cannot find room with code {room_code}")
    else:
        raise KeyError("must provide at least one of room_id or room_code find_room")


# return two things (tuple)
# 1. a tuple of (question_id, question_text)
# 2. a list of pairs (tuple): (choice_id, choice_text)
def create_question(room_code: str, question: str, choices: List[str]) -> Tuple[Tuple[int, str], List[Tuple[int, str]]]:
    room_id = find_room(room_code=room_code).id
    q = insert(PollQuestion).values(room_id=room_id, question=question).returning(PollQuestion.id)
    result = g.session.execute(q)
    q_id = result.fetchall()[0][0]
    new_choices = []
    for choice in choices:
        print(choice)
        q = insert(PollChoice).values(question_id=q_id, choice_text=choice).returning(PollChoice.id)
        result = g.session.execute(q)
        new_choices.append((result.fetchall()[0][0], choice))
    print(new_choices)
    g.session.commit()
    return (q_id, question), new_choices


def log_answer(user_id: int, answer_id):
    q = insert(PollAnswer).values(user_id=user_id, answer_id=answer_id)
    g.session.execute(q)
    g.session.commit()
