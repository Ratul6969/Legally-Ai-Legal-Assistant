import streamlit as st
import json
import requests

# Gemini API Key
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Gemini Model Endpoint
BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generate"

headers = {"Content-Type": "application/json"}

# Cache for API responses
response_cache = {}
feedback_data = "feedback.json"

def get_legal_response(prompt):
    """Fetch legal response from Gemini API with caching."""
    if prompt in response_cache:
        return response_cache[prompt]
    
    formatted_prompt = f"বাংলাদেশের আইন অনুযায়ী শুধুমাত্র বুলেট পয়েন্টে একটি আইনি পরামর্শ দিন:\n\n{prompt}"
    
    payload = {
        "contents": [{"parts": [{"text": formatted_prompt}]}],
        "generationConfig": {"maxOutputTokens": 200}
    }
    
    response = requests.post(f"{BASE_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        response_cache[prompt] = result  # Store in cache
        return result
    return "⚠️ ত্রুটি: আইনি পরামর্শ পাওয়া যায়নি, দয়া করে পুনরায় চেষ্টা করুন।"

def process_legal_query(query):
    """Fetch legal response in Bangla."""
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
        "user_feedback": user_feedback
    }
    try:
        with open(feedback_data, "a") as file:
            json.dump(feedback_entry, file)
            file.write("\n")
    except Exception as e:
        st.error(f"Error saving feedback: {str(e)}")
