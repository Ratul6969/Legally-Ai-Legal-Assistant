import streamlit as st
import json
import requests
import logging
import os

# Configure logging
logging.basicConfig(level=logging.ERROR)

# Set page config (MUST be the first Streamlit command)
st.set_page_config(page_title="Legal Advice Assistant", page_icon="⚖️")

# Gemini API Key (Handle free tier limitations)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.warning("Please enter your Gemini API key in Streamlit secrets.")
    GEMINI_API_KEY = st.text_input("Gemini API Key (Free Tier):", type="password")

# Gemini Model Endpoint
BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generate"

headers = {"Content-Type": "application/json"}

# Cache for API responses (Limit cache size)
response_cache = {}
MAX_CACHE_SIZE = 10

# Feedback data file
feedback_data = "feedback.json"

def get_legal_response(prompt):
    """Fetch legal response from Gemini API with caching and error handling."""
    if not GEMINI_API_KEY:
        return "⚠️ Error: API key not provided."

    if prompt in response_cache:
        return response_cache[prompt]

    formatted_prompt = f"বাংলাদেশের আইন অনুযায়ী শুধুমাত্র বুলেট পয়েন্টে একটি আইনি পরামর্শ দিন:\n\n{prompt}"

    payload = {
        "contents": [{"parts": [{"text": formatted_prompt}]}],
        "generationConfig": {"maxOutputTokens": 200},
    }

    try:
        response = requests.post(
            f"{BASE_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload
        )
        response.raise_for_status()

        result = response.json()["candidates"][0]["content"]["parts"][0]["text"]

        if len(response_cache) >= MAX_CACHE_SIZE:
            oldest_key = next(iter(response_cache))
            del response_cache[oldest_key]

        response_cache[prompt] = result
        return result

    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {e}")
        return "⚠️ Error: API request failed, please try again."
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logging.error(f"API response parsing error: {e}")
        return "⚠️ Error: API response parsing failed."
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return "⚠️ Error: An unexpected error occurred."

def process_legal_query(query):
    """Fetch legal response in Bangla and handle empty queries."""
    if not query.strip():
        return "Please enter a legal query."

    with st.spinner("Fetching legal advice..."):
        response_bn = get_legal_response(query)

    return f"""✅ **Your Legal Advice:**

{response_bn}

⚠️ **Disclaimer:** This is an AI-based legal assistance, not professional legal advice.
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
st.title("Legal Advice Assistant")

user_query = st.text_area("Enter your legal query:")

if st.button("Get Legal Advice"):
    legal_advice = process_legal_query(user_query)
    st.markdown(legal_advice)

    if "✅ **Your Legal Advice:**" in legal_advice:
        feedback = st.radio("Was this advice helpful?", ("Yes", "No"))
        if st.button("Submit Feedback"):
            save_feedback(user_query, legal_advice, feedback)
            st.success("Feedback submitted!")