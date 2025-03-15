import json

import bcrypt
from flask import Flask, jsonify, request
from sqlalchemy.orm import Session

from database import get_db, init_db
from database.models import Chat, Entry, Event, User

init_db()
app = Flask(__name__)


@app.route('/all')
def all():
    return jsonify({"message": "All users"})


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


@app.post('/chats')
def create_chat():
    db: Session = get_db()
    data = json.loads(request.data)
    chat = Chat(**data)
    db.add(chat)
    db.commit()
    return jsonify(chat.to_dict())


@app.post('/chats/entries')
def create_entry_for_chat(chat_id):
    db: Session = get_db()
    data = json.loads(request.data)
    entry = Entry(**data)
    db.add(entry)
    db.commit()

    chat = db.query(Chat).filter(entry.chat_id == chat_id).first()
    if chat:
        chat.last_message = entry.id
        chat.last_message_timestamp = entry.timestamp
        db.commit()

    return jsonify(entry.to_dict())


@app.post('/register')
def register():
    db: Session = get_db()
    data = json.loads(request.data)
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'),
                                    bcrypt.gensalt())
    data['password'] = hashed_password.decode('utf-8')
    user = User(**data)
    db.add(user)
    db.commit()
    return jsonify(user.to_dict())


@app.post('/login')
def login():
    db: Session = get_db()
    data = json.loads(request.data)
    user = db.query(User).filter(User.username == data['username']).first()

    if user and bcrypt.checkpw(data['password'].encode('utf-8'),
                               user.password.encode('utf-8')):
        return jsonify({"message": "Login successful", "user": user.to_dict()})
    else:
        return jsonify({"error": "Invalid username or password"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
