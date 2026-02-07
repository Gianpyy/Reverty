import streamlit as st

def log_message(message: str):
    """
    Logs a message to the conversation log.
    """
    st.session_state.shared_log_string += str(message) + "\n\n"