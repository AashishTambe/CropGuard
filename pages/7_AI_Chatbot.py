import streamlit as st
import os

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="CropGuard AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>

.chat-header {
    background: linear-gradient(135deg, #166534, #22c55e);
    padding: 25px;
    border-radius: 15px;
    color: white;
    margin-bottom: 20px;
}

.chat-header h1 {
    margin: 0;
    font-size: 32px;
}

.chat-header p {
    margin-top: 8px;
    font-size: 16px;
}

.info-box {
    background-color: #f0fdf4;
    border-left: 5px solid #16a34a;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.warning-box {
    background-color: #fff7ed;
    border-left: 5px solid #f97316;
    padding: 15px;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="chat-header">
    <h1>🤖 CropGuard AI Farmer Assistant</h1>
    <p>Ask questions about crops, pests, diseases, weather and basic crop management.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:

    st.header("🌾 Crop Information")

    crop = st.selectbox(
        "Select Crop",
        [
            "Tomato",
            "Potato",
            "Wheat",
            "Rice",
            "Maize",
            "Cotton",
            "Sugarcane",
            "Soybean",
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

    st.markdown("""
    ### 💡 You can ask:

    🌱 Crop problems  
    🐛 Pest identification  
    🦠 Disease symptoms  
    💧 Irrigation  
    🌦️ Weather impact  
    🌾 Crop management  
    🧑‍🌾 General farming guidance
    """)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# WELCOME MESSAGE
# ---------------------------------------------------------
if len(st.session_state.messages) == 0:

    st.markdown("""
    <div class="info-box">
    👋 <b>Welcome to CropGuard AI!</b><br><br>
    I can help you understand common crop diseases, pests,
    weather-related risks and basic crop management.
    </div>
    """, unsafe_allow_html=True)

    st.write("Try asking:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🍅 Tomato leaves turning yellow"):
            st.session_state.messages.append(
                {"role": "user", "content": "My tomato leaves are turning yellow. What could be the reason?"}
            )
            st.rerun()

    with col2:
        if st.button("🐛 Common tomato pests"):
            st.session_state.messages.append(
                {"role": "user", "content": "What are common pests that attack tomato plants?"}
            )
            st.rerun()

    with col3:
        if st.button("💧 Irrigation advice"):
            st.session_state.messages.append(
                {"role": "user", "content": "How should I manage irrigation for my crop?"}
            )
            st.rerun()

# ---------------------------------------------------------
# DISPLAY PREVIOUS MESSAGES
# ---------------------------------------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------
# FARMER AI RESPONSE FUNCTION
# ---------------------------------------------------------
def farmer_ai_response(question, crop, location, season):

    q = question.lower()

    # ---------------- TOMATO ----------------

    if "tomato" in q and ("yellow" in q or "yellowing" in q):

        return """
### 🍅 Possible causes of yellow tomato leaves

Common possibilities include:

- Nutrient deficiency
- Overwatering
- Poor drainage
- Root problems
- Natural ageing of older leaves
- Some fungal diseases

### 🌱 What you can check

1. Check whether the soil is staying excessively wet.
2. Look at the lower and upper leaves separately.
3. Check whether spots or unusual patterns are appearing.
4. Make sure the plant receives sufficient sunlight.
5. Avoid excessive irrigation.

If the yellowing is spreading quickly or is accompanied by spots,
consider getting the crop checked by an agriculture expert.

⚠️ This is general guidance and not a definitive diagnosis.
"""

    # ---------------- PEST ----------------

    if "pest" in q or "insect" in q or "bug" in q:

        return f"""
### 🐛 Pest Management — {crop}

For pest problems, first check:

- The underside of leaves
- New shoots
- Stems
- Flowers
- Fruits

Look for:

- Small insects
- Sticky residue
- Holes in leaves
- Curling leaves
- Discoloration
- Webbing

📍 Location: {location if location else "Not provided"}

🌦️ Season: {season}

If you can identify the insect or upload a clear crop image,
the diagnosis can be made more specifically.
"""

    # ---------------- DISEASE ----------------

    if "disease" in q or "infection" in q or "fungus" in q:

        return f"""
### 🦠 Crop Disease Guidance

For **{crop}**, disease symptoms can depend on:

- Temperature
- Humidity
- Rainfall
- Soil moisture
- Crop growth stage
- Previous disease occurrence

Check the affected leaves carefully for:

- Spots
- Lesions
- Powder-like growth
- Wilting
- Curling
- Unusual discoloration

Do not apply a chemical treatment solely based on a chatbot response.
For a reliable diagnosis, use CropGuard's image detection feature
or consult an agriculture expert.
"""

    # ---------------- WEATHER ----------------

    if "weather" in q or "rain" in q or "humidity" in q or "temperature" in q:

        return f"""
### 🌦️ Weather & Crop Risk

Weather can influence crop disease and pest populations.

For **{crop}**, important factors include:

🌡️ Temperature  
💧 Humidity  
🌧️ Rainfall  
🌱 Soil moisture  
🌬️ Wind conditions

High humidity and prolonged leaf wetness can increase the risk
of several plant diseases.

📍 Your selected location: {location if location else "Not provided"}

For accurate current weather-based risk analysis, CropGuard can
connect this chatbot with its weather/risk-analysis module.
"""

    # ---------------- IRRIGATION ----------------

    if "water" in q or "irrigation" in q:

        return f"""
### 💧 Irrigation Guidance — {crop}

Good irrigation management depends on:

- Crop type
- Soil type
- Weather
- Crop growth stage
- Recent rainfall

Avoid both prolonged waterlogging and unnecessary irrigation.

A useful CropGuard improvement would be to combine soil,
weather and crop-stage information before generating irrigation
recommendations.
"""

    # ---------------- HEALTHY ----------------

    if "healthy" in q or "health" in q:

        return f"""
### 🌱 Crop Health Check

For **{crop}**, regularly monitor:

✅ Leaf colour  
✅ New growth  
✅ Pest activity  
✅ Disease spots  
✅ Soil moisture  
✅ Weather conditions

Early detection is usually easier than dealing with a severe
crop problem later.
"""

    # ---------------- DEFAULT RESPONSE ----------------

    return f"""
### 🌾 CropGuard Assistant

I understand that you are asking about:

**Crop:** {crop}  
**Location:** {location if location else "Not provided"}  
**Season:** {season}

For better guidance, describe:

1. What symptoms are you seeing?
2. Which part of the plant is affected?
3. When did the problem start?
4. Is the problem spreading?
5. What has the recent weather been like?

You can also use the **Farmer Detection** page to analyze a
crop image and then ask questions about the result here.

⚠️ CropGuard provides decision-support information and should
not replace advice from a qualified agriculture professional.
"""

# ---------------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------------
question = st.chat_input(
    "Ask CropGuard about your crop..."
)

# ---------------------------------------------------------
# PROCESS QUESTION
# ---------------------------------------------------------
if question:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(question)

    # Generate response
    answer = farmer_ai_response(
        question,
        crop,
        location,
        season
    )

    # Save response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    # Display response
    with st.chat_message("assistant"):
        st.markdown(answer)

# ---------------------------------------------------------
# CLEAR CHAT
# ---------------------------------------------------------
if st.session_state.messages:

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()