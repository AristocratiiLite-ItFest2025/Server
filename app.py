import os

from flask import Flask, jsonify
from sqlalchemy.orm import Session

from src.database import get_db, init_db
from src.database.models import User

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
