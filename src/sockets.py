from database import queues
from src import socketio


@socketio.on('listen_messages')
def listen_messages(user_id):

    queue_id = f"user_{user_id}"
    queues[queue_id] = []
    queue = queues[queue_id]

    while True:
        if queue:
            message = queue.pop(0)
            socketio.emit('message', message)
        else:
            socketio.sleep(1)
