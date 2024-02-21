from flask import Blueprint, render_template, request, json

from managers import poll_manager
from models.db_models import PollRoom

bp = Blueprint('poll', __name__, url_prefix='/poll')


@bp.route('/admin')
def get_admin_page():
    room_code = create_or_join_room(request.args.get("room_id"), request.args.get("room_code"))
    return render_template("poll_admin.html", room_code=room_code)


@bp.route('/client')
def get_client_page():
    return render_template("poll_client.html", room_code=request.args.get("room_code"))


@bp.post('/create_question')
def create_question():
    print("YES")
    body = request.get_json()
    return poll_manager.create_question(body["room_code"], body["question"], json.loads(body["choices"]))


def create_or_join_room(room_id_str: str, room_code: str):
    try:
        room_id: int = int(room_id_str) if room_id_str is not None else None
        poll_room: PollRoom = poll_manager.find_room(room_id=room_id, room_code=room_code)
        return poll_room.code
    except KeyError:
        poll_room = poll_manager.create_room(name="Hello World")
        return poll_room.code
