import json

import bcrypt
from flask import Flask, jsonify, request
from sqlalchemy.orm import Session

from src import default
from database import get_db
from database.models import User


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
