import os

import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/aristocratii")


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# Create a table and insert sample data
with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                text VARCHAR(255) NOT NULL
            )
        """)
        cur.execute(
            "INSERT INTO messages (text) VALUES ('Hello from PostgreSQL!') ON CONFLICT DO NOTHING;"
        )
        conn.commit()


@app.route('/')
def hello_world():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT text FROM messages LIMIT 1;")
            message = cur.fetchone()
    return jsonify({"message": message})


@app.route('/all')
def all():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM messages;")
            message = cur.fetchall()

    return jsonify(
        {"messages": [{
            "id": i,
            "text": m
        } for i, m in enumerate(message)]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
