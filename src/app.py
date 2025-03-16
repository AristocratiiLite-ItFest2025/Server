import json
from datetime import datetime
from time import time

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from sqlalchemy.orm import Session

from database import get_db, init_db
from database.models import Chat, Entry, Event, User

init_db()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on('message')
def handle_message(data):
    user_id = data["user_id"]
    room = data["chat_id"]
    text = data["text"]

    db_message = Entry(chat_id=data["chat_id"],
                       user_id=data["user_id"],
                       timestamp=datetime.now(),
                       text=data["text"])

    db = get_db()
    db.add(db_message)
    db.commit()

    entry = db_message.to_dict()
    entry["username"] = db.query(User)\
                          .filter(User.id == user_id)\
                          .first().username
    entry["timestamp"] = entry["timestamp"].isoformat()

    entry_json = json.dumps(entry)
    send(entry_json, to=room)

    chat = db.query(Chat).filter(Chat.id == room).first()
    for participant in chat.participants:
        if participant.id != user_id:
            send(entry_json, to=participant.id)


@socketio.on('join')
def on_join(data):
    room = data["chat_id"]

    join_room(room)
    send("User joined", to=room)


@socketio.on('leave')
def on_leave(data):
    room = data["chat_id"]

    leave_room(room)


@socketio.on('listen')
def listen_chats(data):
    user_id = data["user_id"]
    db = get_db()
    chats = db.query(Chat).filter(
        Chat.participants.any(User.id == user_id)).all()

    for chat in chats:
        json_chat = json.dumps(chat.to_dict())
        send(json_chat, to=user_id)

    join_room(user_id)


@app.get('/users')
def get_users():
    db: Session = get_db()
    users = db.query(User).all()
    return jsonify([user.to_dict() for user in users])


@app.get('/events')
def get_events():
    db: Session = get_db()
    events = db.query(Event).all()
    return jsonify([event.to_dict() for event in events])


@app.get('/chats')
def get_chats():
    db: Session = get_db()
    chats = db.query(Chat).all()
    return jsonify([chat.to_dict() for chat in chats])


@app.get('/entries')
def get_entries():
    db: Session = get_db()
    entries = db.query(Entry).all()
    return jsonify([entry.to_dict() for entry in entries])


@app.get('/users/<int:user_id>')
def get_user(user_id):
    db: Session = get_db()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({"error": "User not found"}), 404


@app.get('/events/<int:event_id>')
def get_event(event_id):
    db: Session = get_db()
    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        return jsonify(event.to_dict())
    else:
        return jsonify({"error": "Event not found"}), 404


@app.get('/chats/<int:chat_id>')
def get_chat(chat_id):
    db: Session = get_db()
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat:
        return jsonify(chat.to_dict())
    else:
        return jsonify({"error": "Chat not found"}), 404


@app.get('/entries/<int:chat_id>')
def get_entries_by_chat(chat_id):
    db: Session = get_db()
    entries = db.query(Entry).filter(Entry.chat_id == chat_id).all()
    if entries:
        return jsonify([entry.to_dict() for entry in entries])
    else:
        return jsonify({"error": "No entries found for this chat"}), 404


@app.post('/users')
def create_user():
    db: Session = get_db()
    data = json.loads(request.data)
    user = User(**data)
    db.add(user)
    db.commit()
    return jsonify(user.to_dict())


@app.post('/events')
def create_event():
    db: Session = get_db()
    data = json.loads(request.data)
    event = Event(**data)
    db.add(event)
    db.commit()
    return jsonify(event.to_dict())


@app.post('/entries')
def create_entry():
    db: Session = get_db()
    data = json.loads(request.data)
    entry = Entry(**data)
    db.add(entry)
    db.commit()

    chat = db.query(Chat).filter(Chat.id == entry.chat_id).first()
    if chat:
        chat.last_message = entry.text
        db.commit()

    return jsonify(entry.to_dict())


@app.post('/chats')
def create_chat():
    db: Session = get_db()
    data = json.loads(request.data)
    chat = Chat(**data)
    db.add(chat)
    db.commit()
    return jsonify(chat.to_dict())


@app.post('/register')
def register_user():
    try:
        db: Session = get_db()
        try:
            data = json.loads(request.data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format"}), 400


        required_fields = ['username', 'password', 'email', 'isVerified']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            user = User(**data)
            db.add(user)
            db.commit()
            return jsonify(user.to_dict())
        except Exception as e:
            db.rollback()
            # Check for duplicate username constraint violation
            if "unique constraint" in str(e).lower() and "username" in str(e).lower():
                return jsonify({"error": "Username already exists"}), 409
            return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.post('/login')
def login_user():
    try:
        db: Session = get_db()
        try:
            data = json.loads(request.data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format"}), 400

        # Check required fields
        if "username" not in data or "password" not in data:
            return jsonify({"error": "Username and password are required"}), 400

        try:
            user = db.query(User).filter(User.username == data["username"]).first()
            if user and user.password == data["password"]:
                return jsonify(user.to_dict())
            else:
                return jsonify({"error": "Invalid credentials"}), 401
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500




if __name__ == "__main__":
    socketio.run(app,
                 host="0.0.0.0",
                 port=5000,
                 debug=True,
                 allow_unsafe_werkzeug=True)
    app.run(host="0.0.0.0", port=5000, debug=True, cors_allowed_origins="*")
