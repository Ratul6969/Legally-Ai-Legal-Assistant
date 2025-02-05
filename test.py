import streamlit as st

from googletrans import Translator
import requests

# Hugging Face API Key

HF_API_KEY = st.secrets["HF_API_KEY"]

# Model Endpoints
MISTRAL_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
BASE_URL = "https://api-inference.huggingface.co/models/"

headers = {"Authorization": f"Bearer {HF_API_KEY}"}
translator = Translator()

# Cache for API responses and translations
response_cache = {}
translation_cache = {}

def get_legal_response(prompt):
    """Fetch legal response from Mistral 7B with caching."""
    if prompt in response_cache:
        return response_cache[prompt]
    
    formatted_prompt = f"Provide a legal response based on the laws of Bangladesh only in bullet points:\n\n{prompt}"
    payload = {
        "inputs": formatted_prompt,
        "parameters": {"max_new_tokens": 200},  # Reduce token size for faster response
        "options": {"wait_for_model": False}
    }
    
    response = requests.post(BASE_URL + MISTRAL_MODEL, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()[0]["generated_text"]
        response_cache[prompt] = result  # Store in cache
        return result
    return "Error: Unable to generate response."

def translate_english_to_bangla(english_text):
    """Translate English text to Bangla using Google Translate with caching."""
    if not english_text.strip():
        return "Translation Error: Empty text provided."

    if english_text in translation_cache:
        return translation_cache[english_text]

    try:
        bullet_points = english_text.split("\n")
        translated_points = [
            translator.translate(point.strip(), src="en", dest="bn").text
            for point in bullet_points if point.strip()
        ]
        result = "\n\n".join(translated_points)
        translation_cache[english_text] = result  # Store in cache
        return result
    except Exception:
        return "Translation Error: Unable to process translation."

def process_legal_query(query_bn):
    """Fetch legal response and translate to Bangla."""
    response_en = get_legal_response(query_bn)
    
    if "Error" in response_en:
        return "⚠️ **ত্রুটি:** আইনি পরামর্শ পাওয়া যায়নি, দয়া করে পুনরায় চেষ্টা করুন।"

    translated_response_bn = translate_english_to_bangla(response_en)

    return f"""✅ **আপনার আইনি পরামর্শ:**  

{translated_response_bn}  

⚠️ **ডিসক্লেমার:** এটি একটি AI-ভিত্তিক আইনি সহায়তা, পেশাদার আইনজীবীর পরামর্শ নয়।
"""