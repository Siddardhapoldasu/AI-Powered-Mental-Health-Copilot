import streamlit as st
from openai import OpenAI
from textblob import TextBlob
import pandas as pd
import os

# -----------------------------------------
#  PUT YOUR API KEY HERE (unsafe but works)
# -----------------------------------------
from dotenv import load_dotenv

load_dotenv()
API_KEY=os.getenv("API_KEY")
# <--- Replace this ONLY

client = OpenAI(api_key=API_KEY)

# GPT Response
def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a supportive mental health chatbot."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# Sentiment Analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0.5:
        return "Very Positive", polarity
    elif 0.1 < polarity <= 0.5:
        return "Positive", polarity
    elif -0.1 <= polarity <= 0.1:
        return "Neutral", polarity
    elif -0.5 < polarity < -0.1:
        return "Negative", polarity
    else:
        return "Very Negative", polarity

# Coping Strategies
def provide_coping_strategy(sentiment):
    strategies = {
        "Very Positive": "Keep up the positive energy! Maybe write down what made today great.",
        "Positive": "Nice! Continue doing the things that improve your mood.",
        "Neutral": "Neutral moods happen. Try music, walking, or something you enjoy.",
        "Negative": "Sorry you're feeling down. Try relaxation, journaling, or a short break.",
        "Very Negative": "It sounds tough. Consider talking to a close friend or professional."
    }
    return strategies.get(sentiment, "You're doing your best. Keep going!")

# Sidebar Disclaimer
def display_disclaimer():
    st.sidebar.markdown(
        "<h3 style='color:#34495E;'>Data Privacy Disclaimer</h3>"
        "<p style='color:#7F8C8D;'>Avoid sharing personal or sensitive information.</p>",
        unsafe_allow_html=True
    )

st.title("🧠 Mental Health Support Chatbot")

# Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "mood_tracker" not in st.session_state:
    st.session_state["mood_tracker"] = []

# Chat Input
with st.form("chat_form"):
    user_message = st.text_input("You:")
    submit = st.form_submit_button("Send")

if submit and user_message:
    st.session_state["messages"].append(("You", user_message))

    sentiment, polarity = analyze_sentiment(user_message)
    strategy = provide_coping_strategy(sentiment)

    bot_reply = generate_response(user_message)
    st.session_state["messages"].append(("Bot", bot_reply))

    st.session_state["mood_tracker"].append((user_message, sentiment, polarity))

# Chat History
st.subheader("Chat")
for sender, msg in st.session_state["messages"]:
    st.write(f"{sender}:** {msg}")

# Mood Chart
if st.session_state["mood_tracker"]:
    st.subheader("Mood Trend")
    mood_df = pd.DataFrame(st.session_state["mood_tracker"], columns=["Message", "Sentiment", "Polarity"])
    st.line_chart(mood_df[["Polarity"]])

# Coping Strategy
if submit and user_message:
    st.info(f"Coping Strategy: {strategy}")

# Sidebar
st.sidebar.title("Emergency Resources")
st.sidebar.write("📞 National Suicide Prevention Lifeline: 1-800-273-8255")
st.sidebar.write("📱 Crisis Text Line: Text 'HELLO' to 741741")
st.sidebar.write("[More Help](https://www.mentalhealth.gov/get-help/immediate-help)")

if st.sidebar.button("Show Session Summary"):
    st.sidebar.write("### Your Mood Summary")
    for i, (msg, sent, pol) in enumerate(st.session_state["mood_tracker"]):
        st.sidebar.write(f"{i+1}. {sent} ({pol}) → {msg}")

display_disclaimer()
