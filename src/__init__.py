from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from sqlalchemy.orm import Session

from database import get_db, init_db
from database.models import Chat, Entry, Event, User

init_db()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
