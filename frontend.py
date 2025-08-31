# import streamlit as st
# import speech_recognition as sr
# from gtts import gTTS
# import base64
# import requests
# import uuid
# import os

# # --- Configuration ---
# BACKEND_URL = "http://127.0.0.1:8000/chat"
# MASCOT_IMAGES = {
#     "neutral": "images/neutral.png",
#     "happy": "images/happy.png",
#     "thinking": "images/thinking.gif",
#     "explaining": "images/explaining.png",
# }

# # --- State Management ---
# # Initialize session state variables
# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "mascot_emotion" not in st.session_state:
#     st.session_state.mascot_emotion = "neutral"

# # --- Helper Functions ---
# def get_voice_input():
#     """Captures audio from the microphone and transcribes it to text."""
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         st.info("Listening...")
#         r.adjust_for_ambient_noise(source, duration=0.5)
#         try:
#             audio = r.listen(source, timeout=5, phrase_time_limit=5)
#             text = r.recognize_google(audio)
#             st.success(f"You said: {text}")
#             return text
#         except sr.WaitTimeoutError:
#             st.warning("No speech detected. Please try again.")
#         except sr.UnknownValueError:
#             st.warning("Sorry, I could not understand the audio.")
#         except sr.RequestError as e:
#             st.error(f"Could not request results from speech recognition service; {e}")
#     return None

# def text_to_speech_autoplay(text: str):
#     """Converts text to speech and returns an HTML audio element for autoplay."""
#     if not text:
#         return ""
#     try:
#         tts = gTTS(text=text, lang='en')
#         audio_file = "bot_response.mp3"
#         tts.save(audio_file)
        
#         with open(audio_file, "rb") as f:
#             data = f.read()
#             b64 = base64.b64encode(data).decode()
#             md = f"""
#                 <audio controls autoplay="true" style="display:none;">
#                   <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
#                 </audio>
#                 """
#             st.markdown(md, unsafe_allow_html=True)
#         os.remove(audio_file) # Clean up
#     except Exception as e:
#         st.error(f"Error in TTS: {e}")


# # --- Main UI ---
# st.set_page_config(page_title="AI Tutor", layout="centered")
# st.title("🎓 Your Personal AI Tutor")

# # Mascot Display
# mascot_image_path = MASCOT_IMAGES.get(st.session_state.mascot_emotion, MASCOT_IMAGES["neutral"])
# st.image(mascot_image_path, width=200)

# # Conversation History
# chat_container = st.container(height=300)
# with chat_container:
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

# # User Interaction
# if st.button("🎤 Click to Speak"):
#     st.session_state.mascot_emotion = "thinking"
#     st.rerun() # Update mascot to "thinking" immediately

#     user_query = get_voice_input()
    
#     if user_query:
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": user_query})
        
#         # Display user message in chat container
#         with chat_container:
#             with st.chat_message("user"):
#                 st.markdown(user_query)

#         # Call the backend API
#         try:
#             response = requests.post(
#                 BACKEND_URL,
#                 json={"session_id": st.session_state.session_id, "query": user_query}
#             )
#             response.raise_for_status() # Raise an exception for bad status codes
            
#             api_response = response.json()
#             bot_text = api_response.get("text", "Sorry, something went wrong.")
#             bot_emotion = api_response.get("emotion", "neutral")

#             # Update mascot emotion and add bot message to history
#             st.session_state.mascot_emotion = bot_emotion
#             st.session_state.messages.append({"role": "assistant", "content": bot_text})

#             # Display bot message and play audio
#             with chat_container:
#                 with st.chat_message("assistant"):
#                     st.markdown(bot_text)
#             text_to_speech_autoplay(bot_text)
            
#             st.rerun() # Rerun to update the mascot and chat display

#         except requests.exceptions.RequestException as e:
#             st.error(f"API Error: {e}")
#             st.session_state.mascot_emotion = "neutral"
#             st.rerun()

import streamlit as st
import speech_recognition as sr
import requests
import uuid
from gtts import gTTS
import base64
import os

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000/chat"
MASCOT_EMOJIS = {
    "neutral": "🧑‍🏫", "happy": "😊", "thinking": "🤔", "explaining": "🤓",
}

# --- State Management: Using two separate state variables ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mascot_emotion" not in st.session_state:
    st.session_state.mascot_emotion = "neutral"
if "listening" not in st.session_state:
    st.session_state.listening = False
# The text being actively transcribed (NOT connected to a widget key)
if "live_text" not in st.session_state:
    st.session_state.live_text = ""
# The final text for the text_area (IS connected to a widget key)
if "final_text" not in st.session_state:
    st.session_state.final_text = ""

# --- Callback Functions ---

def start_listening_callback():
    """Activates listening and clears both text states."""
    st.session_state.listening = True
    st.session_state.live_text = ""
    st.session_state.final_text = ""

def stop_listening_callback():
    """Stops listening and copies the live text to the final text area."""
    st.session_state.listening = False
    # This is the key step: copy the result to the widget's state variable
    st.session_state.final_text = st.session_state.live_text
    st.session_state.live_text = ""

def send_to_backend_callback():
    """Sends the final, edited text to the backend."""
    query = st.session_state.final_text
    if not query:
        st.warning("Text box is empty.")
        return

    st.session_state.mascot_emotion = "thinking"
    st.session_state.messages.append({"role": "user", "content": query})

    try:
        response = requests.post(
            BACKEND_URL,
            json={"session_id": st.session_state.session_id, "query": query}
        )
        response.raise_for_status()
        api_response = response.json()
        bot_text = api_response.get("text", "Sorry, something went wrong.")
        bot_emotion = api_response.get("emotion", "neutral")
        st.session_state.mascot_emotion = bot_emotion
        st.session_state.messages.append({"role": "assistant", "content": bot_text})
        text_to_speech_autoplay(bot_text)
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        st.session_state.mascot_emotion = "neutral"
    
    st.session_state.final_text = "" # Clear text box after sending

def text_to_speech_autoplay(text: str):
    if not text: return
    try:
        tts = gTTS(text=text, lang='en')
        audio_file = "bot_response.mp3"
        tts.save(audio_file)
        with open(audio_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"<audio controls autoplay='true' style='display:none;'><source src='data:audio/mp3;base64,{b64}' type='audio/mp3'></audio>"
            st.markdown(md, unsafe_allow_html=True)
        os.remove(audio_file)
    except Exception as e:
        st.error(f"Error in TTS: {e}")

# --- Main UI ---
st.set_page_config(page_title="AI Tutor", layout="centered")
st.title("🎓 Your Personal AI Tutor")

mascot_emoji = MASCOT_EMOJIS.get(st.session_state.mascot_emotion, MASCOT_EMOJIS["neutral"])
st.markdown(f"<p style='font-size: 120px; text-align: center;'>{mascot_emoji}</p>", unsafe_allow_html=True)

st.markdown("### Conversation")
chat_container = st.container(height=300)
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

st.markdown("---")
st.subheader("Your Query")

# The editable text area is now linked to the 'final_text' state
st.text_area("Edit your recognized text here:", key="final_text", height=100)

# Control buttons using the callbacks
col1, col2, col3 = st.columns(3)
with col1:
    st.button("🎤 Start Listening", on_click=start_listening_callback, use_container_width=True)
with col2:
    st.button("🛑 Stop Listening", on_click=stop_listening_callback, use_container_width=True)
with col3:
    st.button("✉️ Send to Tutor", on_click=send_to_backend_callback, use_container_width=True)

# --- The Listening Logic ---
if st.session_state.listening:
    # A placeholder for the live text display
    live_text_placeholder = st.empty()
    live_text_placeholder.info("Listening... Speak now!")

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        while st.session_state.listening:
            try:
                audio = r.listen(source, timeout=2, phrase_time_limit=4)
                recognized = r.recognize_google(audio)
                
                # The loop now ONLY modifies the 'live_text' variable
                st.session_state.live_text += recognized + " "
                live_text_placeholder.markdown(f"> *{st.session_state.live_text}*")

            except sr.WaitTimeoutError: pass
            except sr.UnknownValueError: pass
            except sr.RequestError as e:
                st.error(f"Speech recognition error: {e}")
                st.session_state.listening = False