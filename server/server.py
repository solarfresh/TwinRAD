import eventlet
import eventlet.wsgi
import socketio

try:
    from server.settings import ServerSettings
except ModuleNotFoundError:
    # When running from server directory directly
    from settings import ServerSettings

# Initialize server-specific settings
settings = ServerSettings()

# --- Logger Configuration ---
# Set up basic logging (we'll implement proper logging setup later)
import logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))

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
    print(f"Starting Socket.IO server on {settings.server_host}:{settings.server_port}")
    # Wrap the app in Eventlet's WSGI server
    eventlet.wsgi.server(
        eventlet.listen((settings.server_host, settings.server_port)), app)

def main():
    """Main entry point for the server."""
    run_server()

if __name__ == '__main__':
    main()