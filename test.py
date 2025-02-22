import streamlit as st
import json
import google.generativeai as genai
import logging

# Set page config
st.set_page_config(page_title="Legal Advice Assistant", page_icon="⚖️")
# Configure logging
logging.basicConfig(level=logging.ERROR)



# Load Gemini API Key
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.warning("Please enter your Gemini API key in Streamlit secrets.")
    GEMINI_API_KEY = st.text_input("Gemini API Key (Free Tier):", type="password")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ API key not found! Please add it to Streamlit secrets.")

# Cache for API responses
response_cache = {}
MAX_CACHE_SIZE = 10

# Feedback data file
feedback_data = "feedback.json"

def get_legal_response(prompt):
    """Fetch legal response from Gemini API using Google's SDK."""
    if not GEMINI_API_KEY:
        return "⚠️ Error: API key not provided."

    if prompt in response_cache:
        return response_cache[prompt]

    formatted_prompt = f"বাংলাদেশের আইন অনুযায়ী শুধুমাত্র বুলেট পয়েন্টে একটি আইনি পরামর্শ দিন:\n\n{prompt}"

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(formatted_prompt)

        if response and response.text:
            result = response.text

            # Maintain cache size
            if len(response_cache) >= MAX_CACHE_SIZE:
                oldest_key = next(iter(response_cache))
                del response_cache[oldest_key]

            response_cache[prompt] = result
            return result
        else:
            return "⚠️ Error: No response from Gemini API."

    except Exception as e:
        logging.error(f"API request error: {e}")
        return "⚠️ Error: API request failed, please try again."

def process_legal_query(query):
    """Fetch legal response in Bangla and handle empty queries."""
    if not query.strip():
        return "⚠️ অনুগ্রহ করে একটি আইনি প্রশ্ন লিখুন।"

    with st.spinner("আইনি পরামর্শ সংগ্রহ করা হচ্ছে..."):
        response_bn = get_legal_response(query)

    return f"""✅ **আপনার আইনি পরামর্শ:**  

{response_bn}  

⚠️ **ডিসক্লেমার:** এটি একটি AI-ভিত্তিক আইনি সহায়তা, পেশাদার আইনজীবীর পরামর্শ নয়।
"""

def save_feedback(user_input, model_response, user_feedback):
    """Save user feedback for model improvement."""
    feedback_entry = {
        "user_input": user_input,
        "model_response": model_response,
        "user_feedback": user_feedback,
    }
    try:
        with open(feedback_data, "a") as file:
            json.dump(feedback_entry, file)
            file.write("\n")
    except Exception as e:
        logging.error(f"Error saving feedback: {e}")

# Streamlit UI
st.title("⚖️ Legal Advice Assistant")

user_query = st.text_area("আপনার আইনি প্রশ্ন লিখুন:")

if st.button("আইনি পরামর্শ নিন"):
    legal_advice = process_legal_query(user_query)
    st.markdown(legal_advice)

    if "✅ **আপনার আইনি পরামর্শ:**" in legal_advice:
        feedback = st.radio("এই পরামর্শটি কি আপনার জন্য সহায়ক ছিল?", ("হ্যাঁ", "না"))
        if st.button("মতামত পাঠান"):
            save_feedback(user_query, legal_advice, feedback)
            st.success("মতামত পাঠানো হয়েছে!")
