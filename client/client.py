import streamlit as st
import time
import socketio
from socketio.exceptions import ConnectionError

from configs.logging_config import setup_logging
from configs.settings import settings

test_variable = "This is a test variable for the client."
session_state = {
    'connected': False,
    'messages': []
}

# --- Logger Configuration ---
logger = setup_logging(name='[client]')

# --- Streamlit Session State ---
sio = socketio.Client()

# --- Streamlit UI ---
st.title("Twinrad Client UI")
st.markdown("Connect to the Socket.IO server and send messages.")

# --- Socket.IO Client Event Handlers ---
@sio.event
def connect():
    logger.info("Connection established!")
    session_state["connected"] = True
    session_state["messages"].append(("client", "Connected to the server."))
    # No st.rerun() here, as the main loop handles display

@sio.event
def response(data):
    logger.info(f"Received response from server: {data}")
    session_state["messages"].append(("server", data))
    # We must rerun the app to update the UI
    # st.rerun()

@sio.event
def disconnect():
    logger.info("Disconnected from the server.")
    session_state["connected"] = False
    session_state["messages"].append(("client", "Disconnected from the server."))
    # Rerun to update the UI
    st.rerun()

# --- Main App Logic ---
def run_sio_client():
    """Function to run the Socket.IO client in a separate thread."""
    try:
        # Connect to the server. This is a blocking call.
        logger.info("Attempting to connect to the server...")
        sio.connect(f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}')
        # Wait for the connection to be established
        while not session_state["connected"]:
            # Sleep to allow the connection to establish
            time.sleep(1)
        # session_state.sio.wait()
    except ConnectionError as e:
        logger.error(f"Failed to connect to server: {e}")
        session_state["messages"].append(("client", f"Failed to connect to server: {e}"))
        session_state["connected"] = False

def main():
    if not ('connected' in session_state and session_state["connected"]):
        st.info("Attempting to connect to the server...")
        run_sio_client()
        # st.rerun()

    # Display status
    if session_state["connected"]:
        st.success("Connected to the server!")
    else:
        st.warning("Not connected to the server.")

    # Text input and button for sending messages
    user_input = st.text_input("Enter a message to send to the server:")
    if st.button("Send Message") and user_input and session_state["connected"]:
        sio.emit('message', user_input)
        session_state["messages"].append(("client", f"Message sent: {user_input}"))

    time.sleep(1)

    # Display the message history
    for sender, message in session_state["messages"]:
        if sender == "client":
            st.info(message, icon="👨‍💻")
        else:
            st.success(message, icon="🤖")

if __name__ == '__main__':
    main()