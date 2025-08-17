import eventlet
import eventlet.wsgi
import socketio

from configs.settings import settings
from configs.logging_config import setup_logging

# --- Logger Configuration ---
# Set up the logger using the centralized config function
logger = setup_logging(name='[server]')

# --- Socket.IO Server ---

# Create a Socket.IO server instance
sio = socketio.Server(async_mode='eventlet')

# Create a WSGI application
app = socketio.WSGIApp(sio)

# Define event handlers
@sio.event
def connect(sid, environ):
    """
    Handles a new client connection.
    `sid` is the unique session ID for the client.
    `environ` contains connection details.
    """
    print(f"Client connected: {sid}")

@sio.event
def disconnect(sid):
    """
    Handles a client disconnection.
    """
    print(f"Client disconnected: {sid}")

@sio.event
def message(sid, data):
    """
    Handles an incoming 'message' event from a client.
    `sid` is the session ID.
    `data` is the message content.
    """
    print(f"Received message from {sid}: {data}")
    # Here you can add logic to route the message to other agents
    sio.emit('response', f"Server received your message: {data}", room=sid)

@sio.event
def response_event(sid, data):
    """
    """
    print(f"Received response_event from {sid} with data: {data}")
    sio.emit('response', f"Server received your message: {data}", room=sid)

def run_server():
    """
    Runs the Socket.IO server.
    """
    print("Starting Socket.IO server on localhost:5000")
    # Wrap the app in Eventlet's WSGI server
    eventlet.wsgi.server(
        eventlet.listen((settings.SERVER_HOST, settings.SERVER_PORT)), app)

if __name__ == '__main__':
    run_server()