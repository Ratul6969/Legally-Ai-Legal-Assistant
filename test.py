import streamlit as st
import json
import requests
import logging
import os

# Configure logging
logging.basicConfig(level=logging.ERROR)  # Log errors only

# Gemini API Key (Handle free tier limitations)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.warning("Please enter your Gemini API key in Streamlit secrets.")
    GEMINI_API_KEY = st.text_input("Gemini API Key (Free Tier):", type="password")  # Allow manual input for free tier

# Gemini Model Endpoint
BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generate"

headers = {"Content-Type": "application/json"}

# Cache for API responses (Limit cache size)
response_cache = {}
MAX_CACHE_SIZE = 10  # Limit cache to 10 entries

# Feedback data file
feedback_data = "feedback.json"

def get_legal_response(prompt):
    """Fetch legal response from Gemini API with caching and error handling."""
    if not GEMINI_API_KEY:  # Handle missing API key
        return "⚠️ ত্রুটি: API কী প্রদান করা হয়নি।"

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
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        result = response.json()["candidates"][0]["content"]["parts"][0]["text"]

        # Cache management: Evict oldest entry if cache is full
        if len(response_cache) >= MAX_CACHE_SIZE:
            oldest_key = next(iter(response_cache))
            del response_cache[oldest_key]

        response_cache[prompt] = result  # Store in cache
        return result

    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {e}")
        return "⚠️ ত্রুটি: API অনুরোধে সমস্যা হয়েছে, পুনরায় চেষ্টা করুন।"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logging.error(f"API response parsing error: {e}")
        return "⚠️ ত্রুটি: API প্রতিক্রিয়ায় সমস্যা হয়েছে।"
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return "⚠️ ত্রুটি: একটি অপ্রত্যাশিত ত্রুটি ঘটেছে।"

def process_legal_query(query):
    """Fetch legal response in Bangla and handle empty queries."""
    if not query.strip():  # Check for empty or whitespace-only input
        return "অনুগ্রহ করে একটি আইনি প্রশ্ন লিখুন।"

    with st.spinner("আইনি পরামর্শ খোঁজা হচ্ছে..."):
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
        logging.error(f"Error saving feedback: {e}") #Log error, don't show to user.

# Streamlit UI
st.title("আইনি পরামর্শ সহকারী")

user_query = st.text_area("আপনার আইনি প্রশ্ন লিখুন:")

if st.button("আইনি পরামর্শ নিন"):
    legal_advice = process_legal_query(user_query)
    st.markdown(legal_advice)

    if "✅ আপনার আইনি পরামর্শ:" in legal_advice: #only provide feedback option if there was a response.
        feedback = st.radio("এই পরামর্শ কি সহায়ক ছিল?", ("হ্যাঁ", "না"))
        if st.button("ফিডব্যাক জমা দিন"):
            save_feedback(user_query, legal_advice, feedback)
            st.success("ফিডব্যাক জমা দেওয়া হয়েছে!")