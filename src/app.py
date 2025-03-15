import os
from datetime import datetime, timedelta

from flask import Flask, jsonify
from sqlalchemy.orm import Session

from database import get_db, init_db
from database.models import User, Chat, Entry, Event

init_db()
app = Flask(__name__)


@app.route('/')
def hello_world():
    db: Session = get_db()
    user = User(username="test", password="test")
    db.add(user)
    user = db.query(User).filter(User.username == "test").first()
    name = user.username

    return jsonify({"message": f"Hello, {name}!"})


@app.route('/all')
def all():
    return jsonify({"message": "All users"})

@app.route('/users')
def get_users():
    db: Session = get_db()
    users = db.query(User).all()
    return jsonify([user.__dict__ for user in users])




@app.route('/events')
def get_events():
    db: Session = get_db()
    events = db.query(Event).all()
    return jsonify([event.__dict__ for event in events])

@app.route('/chats')
def get_chats():
    db: Session = get_db()
    chats = db.query(Chat).all()
    return jsonify([chat.__dict__ for chat in chats])

@app.route('/entries')
def get_entries():
    db: Session = get_db()
    entries = db.query(Entry).all()
    return jsonify([entry.__dict__ for entry in entries])

@app.route('/insert')
def insert_mock_data():
    db: Session = get_db()

    # Mock data for User
    users = [
        User(username="user1", password="hashed_password1", email="user1@example.com", bani_sold=100.0,
             isVerifiedNGO=True, isVerifiedSponsor=False, isVerifiedPerson=True, isPublic=True,
             avatar_image="avatar1.png"),
        User(username="user2", password="hashed_password2", email="user2@example.com", bani_sold=200.0,
             isVerifiedNGO=False, isVerifiedSponsor=True, isVerifiedPerson=False, isPublic=False,
             avatar_image="avatar2.png"),
        User(username="user3", password="hashed_password3", email="user3@example.com", bani_sold=300.0,
             isVerifiedNGO=False, isVerifiedSponsor=False, isVerifiedPerson=True, isPublic=True,
             avatar_image="avatar3.png")
    ]
    db.add_all(users)
    db.commit()
    # Mock data for Event
    events = [
        Event(lat=40.7128, lon=-74.0060, name="Event1", short_description="Short desc 1",
              attendees="1,2", long_description="Long desc 1", author_id=1,
              email_for_contact="user1@example.com", phone_contact="1234567890",
              start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2),
              image="image1.png", icon_image="icon1.png", recurring_duration="weekly"),
        Event(lat=34.0522, lon=-118.2437, name="Event2", short_description="Short desc 2",
              attendees="2,3", long_description="Long desc 2", author_id=2,
              email_for_contact="user2@example.com", phone_contact="0987654321",
              start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=3),
              image="image2.png", icon_image="icon2.png", recurring_duration="monthly")
    ]
    db.add_all(events)
    db.commit()

    # Mock data for Chat
    chats = [
        Chat(last_message_timestamp=datetime.now(), last_message="Hello World", name="Chat1", chat_image="chat1.png"),
        Chat(last_message_timestamp=datetime.now(), last_message="Hi there", name="Chat2", chat_image="chat2.png")
    ]

    # Insert mock data into the database


    db.add_all(chats)
    db.commit()

    # Mock data for Entry
    entries = [
        Entry(chat_id=1, user_id=1, timestamp=datetime.now(), text="Entry text 1"),
        Entry(chat_id=1, user_id=2, timestamp=datetime.now(), text="Entry text 2"),
        Entry(chat_id=2, user_id=3, timestamp=datetime.now(), text="Entry text 3")
    ]

    # Insert entries into the database
    db.add_all(entries)
    db.commit()

    return jsonify({"message": "Mock data inserted successfully!"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
