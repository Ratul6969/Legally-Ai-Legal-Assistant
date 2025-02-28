import streamlit as st
import pandas as pd
import os
from test import process_legal_query
import hashlib

# Configure page settings
st.set_page_config(
    page_title="Legally - AI Legal Assistant",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Feedback storage file
FEEDBACK_FILE = "feedback.csv"

def save_feedback(question, response, feedback_text, rating):
    """Save user feedback to a CSV file."""
    feedback_data = pd.DataFrame([{"Question": question, "Response": response, "Feedback": feedback_text, "Rating": rating}])
    
    if os.path.exists(FEEDBACK_FILE):
        feedback_data.to_csv(FEEDBACK_FILE, mode='a', header=False, index=False)
    else:
        feedback_data.to_csv(FEEDBACK_FILE, mode='w', header=True, index=False)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}

# Chat interface
st.title("⚖️ Legally - AI Legal Assistant")
st.subheader("আইন আপনার হাতের মুঠোয়।")

# User input
with st.form(key='chat_form'):
    user_input = st.text_input("আপনার আইনি প্রশ্নটি লিখুন:", "")
    submitted = st.form_submit_button("পরামর্শ পান")

if submitted and user_input:
    if user_input in st.session_state.response_cache:
        response = st.session_state.response_cache[user_input]
    else:
        with st.spinner('প্রক্রিয়াকরণ হচ্ছে...'):
            response = process_legal_query(user_input)
            st.session_state.response_cache[user_input] = response
    
    st.session_state.conversation_history.append({"question": user_input, "response": response})

# Display conversation history
if st.session_state.conversation_history:
    for chat in reversed(st.session_state.conversation_history):
        
        st.markdown(f"**আপনি:** {chat['question']}")
        st.markdown(f"**Legally:** {chat['response']}")
        
        
        # Generate unique keys for feedback widgets by hashing the question
        unique_key = hashlib.md5(chat['question'].encode('utf-8')).hexdigest()

        # Feedback section
        with st.expander("🔄 মতামত দিন"):
            rating = st.radio("উত্তরের মান কেমন ছিল?", ["ভাল", "গড়", "দুর্বল"], key=f"rating_{unique_key}")
            feedback_text = st.text_area("আপনার পরামর্শ (ঐচ্ছিক):", key=f"feedback_{unique_key}")
            if st.button("প্রেরণ", key=f"submit_feedback_{unique_key}"):
                save_feedback(chat['question'], chat['response'], feedback_text, rating)
                st.success("ধন্যবাদ! আপনার মতামত গ্রহণ করা হয়েছে।")

if __name__ == "__main__":
    st.write("\n")
