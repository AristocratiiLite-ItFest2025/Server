import json
from datetime import datetime
from time import time
import os
from pprint import pprint
import uuid
from flask import Flask, jsonify, request, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from sqlalchemy.orm import Session, column_property

from database import get_db, init_db
from database.models import Chat, Entry, Event, User

# Add this near the top, after other imports
UPLOAD_FOLDER = 'src/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

init_db()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post('/upload-image')
def upload_image():
    try:
        # Check if the request has the file part
        if 'image' not in request.files:
            return jsonify({"error": "No image part in the request"}), 400

        file = request.files['image']

        # If user does not select file, browser submits an empty file
        if file.filename == '':
            return jsonify({"error": "No image selected"}), 400

        if file and allowed_file(file.filename):
            # Create a secure unique filename
            original_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{original_extension}"


            # Save the file
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            unique_filename = unique_filename.split('.')[0]
            # Generate the URL to access the image
            # Assuming the app is served at the root path
            image_url = f"/images/{unique_filename}"

            return jsonify({
                "message": "Image uploaded successfully",
                "url": image_url
            })
        else:
            return jsonify({"error": "File type not allowed"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.get('/images')
def list_images():
    try:
        # List all files in the upload directory
        files = os.listdir(UPLOAD_FOLDER)
        images = [f for f in files if allowed_file(f)]
        return jsonify(images)
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Add a route to serve the images
@app.get('/images/<string:filename>')
def get_image(filename):
    # Find the file with the matching UUID prefix
    try:
        # List all files in the upload directory
        files = os.listdir(UPLOAD_FOLDER)

        # Find the file that starts with the provided filename (UUID)
        matching_files = [f for f in files if f.startswith(filename + '.')]

        if not matching_files:
            return jsonify({"error": "File not found"}), 404

        # Get the first matching file
        file = matching_files[0]
        URL= 'uploads'
        return send_file(os.path.join(URL,file),
                         mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@socketio.on('message')
def handle_message(data):
    user_id = data["user_id"]
    chat_id = data["chat_id"]
    room = f"CHAT{chat_id}"

    db_message = Entry(chat_id=data["chat_id"],
                       user_id=data["user_id"],
                       timestamp=datetime.now(),
                       text=data["text"])

    db = get_db()
    db.add(db_message)
    db.commit()

    entry = db_message.to_dict()

    entry_json = json.dumps(entry)
    send(entry_json, to=room)

    chat = db.query(Chat).filter(Chat.id == room).first()
    for participant in chat.participants:
        if participant.id != user_id:
            send(entry_json, to=f"USER{participant.id}")


@socketio.on('join')
def on_join(data):
    chat_id = data["chat_id"]
    room = f"CHAT{chat_id}"

    db = get_db()
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        print(f"Chat {chat_id} not found")
        chat = Chat(id=chat_id, name=f"Chat {chat_id}")

    chat.participants.append(
        db.query(User).filter(User.id == data["user_id"]).first())

    db.add(chat)
    db.commit()

    join_room(room)


@socketio.on('leave')
def on_leave(data):
    chat_id = data["chat_id"]
    room = f"CHAT{chat_id}"

    leave_room(room)


@socketio.on('listen')
def listen_chats(data):
    user_id = data["user_id"]
    room = f"USER{user_id}"

    db = get_db()
    chats = db.query(Chat).filter(
        Chat.participants.any(User.id == user_id)).all()

    join_room(room)

    for chat in chats:
        json_chat = json.dumps(chat.to_dict())
        send(json_chat, to=room)


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


@app.get('/events/<int:user_id>')
def get_events_for_user(user_id):
    db: Session = get_db()

    user = db.query(User).filter(User.id == user_id).first()

    if user:
        return jsonify([event.to_dict() for event in user.events])

    return {"error": "User not found"}, 404


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

@app.post('/users/<int:user_id>/update-verification')
def update_user_verification(user_id):
    try:
        db: Session = get_db()

        # Check if the user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        try:
            data = json.loads(request.data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format"}), 400

        # Check if isVerified is in the request
        if "isVerified" not in data:
            return jsonify({"error": "isVerified field is required"}), 400

        # Validate the isVerified value
        new_status = data["isVerified"]
        valid_statuses = ['NGO', 'SPONSOR', 'PERSON']
        if new_status not in valid_statuses:
            return jsonify({
                "error": f"Invalid verification status. Must be one of: {', '.join(valid_statuses)}"
            }), 400

        # Update the user
        user.isVerified = new_status
        db.commit()

        # Return the updated user
        return jsonify(user.to_dict())
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

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


@app.post('/events/<int:event_id>/join')
def join_event(event_id):
    db: Session = get_db()
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        return jsonify({"error": "Event not found"}), 404

    data = json.loads(request.data)
    user_id = data["user_id"]
    user = db.query(User).filter(User.id == user_id).first()

    event.attendees.append(user)
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
                return jsonify({"error":
                                f"Missing required field: {field}"}), 400

        try:
            user = User(**data)
            db.add(user)
            db.commit()
            return jsonify(user.to_dict())
        except Exception as e:
            db.rollback()
            # Check for duplicate username constraint violation
            if "unique constraint" in str(e).lower() and "username" in str(
                    e).lower():
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
            return jsonify({"error":
                            "Username and password are required"}), 400

        try:
            user = db.query(User).filter(
                User.username == data["username"]).first()
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
