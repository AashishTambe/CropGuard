import streamlit as st
from openai import OpenAI

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="CropGuard AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------
# OPENAI CLIENT
# --------------------------------------------------

try:
    client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )
except Exception:
    client = None

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.chat-title {
    background: linear-gradient(135deg, #166534, #22c55e);
    padding: 25px;
    border-radius: 16px;
    color: white;
    margin-bottom: 25px;
}

.chat-title h1 {
    margin-bottom: 5px;
}

.chat-title p {
    margin: 0;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="chat-title">

<h1>🤖 CropGuard AI Farmer Assistant</h1>

<p>
Your intelligent assistant for crops, diseases, pests,
weather and crop management.
</p>

</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("🌾 Farmer Information")

    crop = st.selectbox(
        "Crop",
        [
            "Tomato",
            "Potato",
            "Rice",
            "Wheat",
            "Maize",
            "Cotton",
            "Soybean",
            "Sugarcane",
            "Other"
        ]
    )

    location = st.text_input(
        "📍 Location",
        placeholder="Example: Kolhapur, Maharashtra"
    )

    season = st.selectbox(
        "🌦️ Season",
        [
            "Kharif",
            "Rabi",
            "Summer",
            "Other"
        ]
    )

    st.divider()

    st.caption(
        "CropGuard AI provides decision-support information. "
        "For serious crop problems, consult a qualified "
        "agriculture professional."
    )

# --------------------------------------------------
# SYSTEM INSTRUCTIONS
# --------------------------------------------------

SYSTEM_PROMPT = f"""
You are CropGuard AI, an agricultural assistant designed
to help farmers understand crop diseases, pests, weather
risks and basic crop management.

The farmer's current information is:

Crop: {crop}
Location: {location if location else "Not provided"}
Season: {season}

Your responsibilities:

1. Answer the farmer naturally and conversationally.
2. Understand follow-up questions using the conversation history.
3. Give practical, easy-to-understand agricultural guidance.
4. Explain possible causes before giving recommendations.
5. Ask clarifying questions when important information is missing.
6. Never pretend that a diagnosis is certain without enough evidence.
7. Do not invent weather data, soil data, disease diagnoses,
   pesticide information or other facts.
8. When discussing crop disease, explain that image-based or
   expert confirmation may be necessary.
9. Prefer integrated pest-management and safe agricultural practices.
10. Keep answers understandable for farmers rather than using
    unnecessarily technical language.
11. If the farmer's question is unrelated to agriculture,
    politely explain that you are CropGuard AI and redirect
    the conversation toward agricultural assistance.
"""

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []

# --------------------------------------------------
# WELCOME MESSAGE
# --------------------------------------------------

if len(st.session_state.messages) == 0:

    st.markdown("""
    ### 👋 Welcome to CropGuard AI

    You can ask me things like:

    - 🌱 Why are my crop leaves turning yellow?
    - 🐛 What could be causing holes in my leaves?
    - 🌦️ How can humidity affect my crop?
    - 💧 How should I think about irrigation?
    - 🦠 What symptoms are associated with common crop diseases?
    - 🌾 How can I monitor my crop?
    """)

# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_question = st.chat_input(
    "Ask CropGuard AI about your crop..."
)

# --------------------------------------------------
# GENERATE AI RESPONSE
# --------------------------------------------------

if user_question:

    # Check API connection
    if client is None:

        st.error(
            "OpenAI API is not configured. "
            "Please check your .streamlit/secrets.toml file."
        )

        st.stop()

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    # Display user message
    with st.chat_message("user"):

        st.markdown(user_question)

    # Prepare conversation
    conversation = [
        {
            "role": "developer",
            "content": SYSTEM_PROMPT
        }
    ]

    conversation.extend(
        st.session_state.messages
    )

    # Generate response
    with st.chat_message("assistant"):

        with st.spinner("🌱 CropGuard AI is thinking..."):

            try:

                response = client.responses.create(
                    model="gpt-5.6-luna",
                    input=conversation
                )

                answer = response.output_text

                st.markdown(answer)

                # Save AI response
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                st.error(
                    "Unable to connect to the AI service."
                )

                st.caption(
                    f"Error: {str(e)}"
                )

# --------------------------------------------------
# CLEAR CHAT
# --------------------------------------------------

if len(st.session_state.messages) > 0:

    st.divider()

    if st.button("🗑️ Clear Conversation"):

        st.session_state.messages = []

        st.rerun()