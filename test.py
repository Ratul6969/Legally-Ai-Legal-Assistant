import streamlit as st
import json
import google.generativeai as genai
import logging

# Set page config
st.set_page_config(page_title="Legal Advice Assistant", page_icon="⚖️")
# Configure logging
logging.basicConfig(level=logging.ERROR)

# Load Gemini API Key from Streamlit secrets or ask the user to input it
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.warning("Please enter your Gemini API key in Streamlit secrets.")
    GEMINI_API_KEY = st.text_input("Gemini API Key (Free Tier):", type="password")
    
    # Check if the user has provided the API key manually
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    else:
        st.error("⚠️ API key not found! Please add it to Streamlit secrets or enter it manually.")

# Cache for API responses
response_cache = {}
MAX_CACHE_SIZE = 10

# Feedback data file
feedback_data = "feedback.json"

def get_legal_response(prompt):
    """Fetch legal response focused on Bangladesh's Constitution and relevant laws."""
    if not GEMINI_API_KEY:
        return "⚠️ Error: API key not provided."

    if prompt in response_cache:
        return response_cache[prompt]

    # Tailored query focusing on Bangladesh's legal context
    formatted_prompt = f"""
    আপনি বাংলাদেশের সংবিধান এবং আইন সম্পর্কে আইনি সহায়তা চান। আমি বাংলাদেশের আইনি প্রসঙ্গ অনুযায়ী আপনার প্রশ্নের জন্য বিস্তারিত ব্যাখ্যা দেব।

    দয়া করে মনে রাখবেন যে আমি শুধুমাত্র বাংলাদেশের সংবিধান, দণ্ডবিধি, এবং অন্যান্য বাংলাদেশের আইনের উপর ভিত্তি করে উত্তর দেব।

    প্রশ্ন: "{prompt}"
    """

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
    """Fetch legal response for Bangladesh-specific laws and handle empty queries."""
    if not query.strip():
        return "⚠️ অনুগ্রহ করে একটি আইনি প্রশ্ন লিখুন।"

    # Check for serious or emergency queries and provide relevant advice
    serious_keywords = ["threat", "rape", "violence", "murder", "emergency", "attack", "abuse"]
    if any(keyword in query.lower() for keyword in serious_keywords):
        return """⚠️ **এটি একটি জরুরি পরিস্থিতি মনে হচ্ছে!**

আপনি যদি হুমকি বা সহিংসতা সম্মুখীন হন, দয়া করে 999 নম্বরে কল করুন অথবা কাছের পুলিশ স্টেশনে যোগাযোগ করুন।

আপনার পরিস্থিতি খুবই গম্ভীর, এবং আমরা জানি এটি আপনাকে খুব বেশি চাপ দিচ্ছে। দয়া করে নিরাপদ থাকুন এবং আপনার কাছে সাহায্য পেতে দ্বিধা করবেন না। আপনার নিরাপত্তা আমাদের প্রথম অগ্রাধিকার। আমরা আপনার পাশে আছি।

এটি একটি AI-ভিত্তিক পরামর্শ, এবং আপনি একজন পেশাদার আইনজীবীর সাথে যোগাযোগ করার পরামর্শ দেয়া হচ্ছে।
"""
    
    with st.spinner("আইনি পরামর্শ সংগ্রহ করা হচ্ছে..."):
        response_bn = get_legal_response(query)

    # Human-like, comforting tone
    return f"""✅ **আপনার আইনি পরামর্শ:**  

{response_bn}  

⚠️ **ডিসক্লেমার:** এটি একটি AI-ভিত্তিক আইনি সহায়তা, পেশাদার আইনজীবীর পরামর্শ নয়।

আমরা জানি আপনি একটি গুরুত্বপূর্ণ প্রশ্ন করেছেন এবং আমরা চেষ্টা করেছি আপনার সমস্যা অনুযায়ী সঠিক পরামর্শ দেওয়ার। যদি আপনার আরও সাহায্যের প্রয়োজন হয়, দয়া করে পেশাদার আইনি সাহায্য গ্রহণ করুন।
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
