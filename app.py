import streamlit as st
from test import process_legal_query

# Configure page settings
st.set_page_config(
    page_title="Legally - AI Legal Assistant",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced UI
def load_css():
    st.markdown(f"""
    <style>
        /* Base styles */
        .stApp {{
            background-color: {'#1a1d24' if st.session_state.dark_mode else '#f8f9fa'};
            color: {'#ffffff' if st.session_state.dark_mode else '#1a1a1a'};
            font-size: 0.95rem;
        }}
        
        /* Main container */
        .main-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }}
        
        /* Header section */
        .header {{
            text-align: center;
            margin-bottom: 2.5rem;
        }}
        
        /* Quick actions grid */
        .quick-actions {{ 
            display: grid;
            grid-template-columns: repeat(2, 1fr); /* Force 2 columns */
            grid-template-rows: repeat(2, auto); /* Force 2 rows */
            gap: 1rem;
            max-width: 500px; /* Prevents single column stacking */
            margin: auto;
            justify-content: center; /* Center the grid */
        }}

        
        .action-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.25rem;
            margin: 0.15rem;
            border: 1px solid var(--card-border);
            transition: transform 0.2s;
            
            
        }}
        
        .action-card:hover {{
            transform: translateY(-2.5px);
        }}
        
        /* Chat interface */
        .chat-container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .user-message {{
            background: {'#2d5278' if st.session_state.dark_mode else '#e3f2fd'};
            color: {'#ffffff' if st.session_state.dark_mode else '#1a1a1a'};
            border-radius: 15px;
            padding: 1rem 1.5rem;
            margin: 0.75rem 0;
            max-width: 75%;
            float: right;
            clear: both;
            font-size: 0.9rem;
        }}
        
        .bot-message {{
            background: {'#2d323b' if st.session_state.dark_mode else '#ffffff'};
            color: {'#ffffff' if st.session_state.dark_mode else '#1a1a1a'};
            border: 1px solid {'#3d424a' if st.session_state.dark_mode else '#e0e0e0'};
            border-radius: 15px;
            padding: 1rem 1.5rem;
            margin: 0.75rem 0;
            max-width: 75%;
            float: left;
            clear: both;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            font-size: 0.9rem;
        }}
        
        /* Input area */
        .stTextInput>div>div>input {{
            border-radius: 25px;
            padding: 0.8rem 1.2rem;
            font-size: 0.9rem;
            background: {'#2d323b' if st.session_state.dark_mode else '#ffffff'};
            border-color: {'#3d424a' if st.session_state.dark_mode else '#e0e0e0'};
        }}
        
        /* Buttons */
        .stButton>button {{
            border-radius: 15px;
            padding: 0.6rem 1.5rem;
            background-color: {'#3b82f6' if st.session_state.dark_mode else '#1d4ed8'};
            color: white;
            font-size: 0.9rem;
            border: none;
            transition: all 0.2s;
        }}
        
        .stButton>button:hover {{
            background-color: {'#2563eb' if st.session_state.dark_mode else '#1e40af'};
            color: #e0e0e0;
            transform: scale(0.98);
        }}
        
        /* Theme toggle */
        .theme-toggle {{
        
            position: fixed;
            margin-top: 3rem;
            top: 1rem;
            right: 1rem;
            z-index: 999;
        }}
    </style>
    """, unsafe_allow_html=True)

# Initialize session state with caching
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "response_cache" not in st.session_state:  # New cache store
    st.session_state.response_cache = {}

# Theme configuration
def update_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Theme toggle component
def theme_toggle():
    st.markdown(f"""
    <div class="theme-toggle">
        <button onclick="updateTheme()" style="
            background: {'#2d323b' if st.session_state.dark_mode else '#ffffff'};
            color: {'#ffffff' if st.session_state.dark_mode else '#1a1a1a'};
            border: 1px solid {'#3d424a' if st.session_state.dark_mode else '#e0e0e0'};
            border-radius: 15px;
            width: 40px;
            height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            {'🌙' if st.session_state.dark_mode else '☀️'}
        </button>
    </div>
    <script>
    function updateTheme() {{
        parent.window.dispatchEvent(new CustomEvent("theme-toggle"));
    }}
    </script>
    """, unsafe_allow_html=True)

# Main app function
def main():
    # Load CSS and theme
    load_css()
    theme_toggle()
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="header">
            <h1 style="font-size: 2.72rem; margin-bottom: 0.5rem;">
                ⚖️ Legally
            </h1>
            <p style="color: #94a3b8; font-size: 0.95rem;">
                আইন আপনার হাতের মুঠোয়।
            </p>
                 <p style="color: #94a3b8; font-size: 0.95rem;">
                Sample Questions
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Quick actions grid
    questions = [
        ("ভাড়াটিয়াদের অধিকার", "বাংলাদেশে ভাড়াটিয়াদের আইনি অধিকার কী?"),
        ("জমি দখল", "যদি আমার জমি দখল হয়ে যায়, তাহলে আমি কি করতে পারি?"),
        ("মিথ্যা অভিযোগ", "কোন পরিস্থিতিতে মিথ্যা অভিযোগের বিরুদ্ধে আইনি পদক্ষেপ নেওয়া যায়?"),
        ("নারী ও শিশু", "বাংলাদেশে নারী ও শিশুদের নিরাপত্তা সম্পর্কিত আইন কী?")
    ]
    
    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
    for title, question in questions:
        if st.markdown(f"""
        <div class="action-card" onclick="document.getElementById('{title}').click()">
            <div style="font-weight: 500; margin-bottom: 0.5rem;">{title}</div>
            <div style="color: {'#94a3b8' if st.session_state.dark_mode else '#64748b'}; font-size: 0.85rem;">{question}</div> 
                      
           <button id="{title}" style="display: none;" data-question="{question}"></button>
        </div>
        """, unsafe_allow_html=True):
            st.session_state.auto_question = question
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat interface with optimized API calls
    with st.form(key='chat_form'):
        user_input = st.text_input(
            '',
            placeholder='আপনার আইনি প্রশ্নটি এখানে লিখুন...',
            key='input',
            value=st.session_state.pop('auto_question', '')
        )
        submitted = st.form_submit_button('পরামর্শ পান')

    if submitted and user_input:
        # Check cache first
        if user_input in st.session_state.response_cache:
            response = st.session_state.response_cache[user_input]
            st.session_state.conversation_history.append({
                'question': user_input,
                'response': response
            })
        else:
            # Only make API call if not in cache
            with st.spinner('প্রশ্ন বিশ্লেষণ করা হচ্ছে...'):
                try:
                    response = process_legal_query(user_input)
                    # Cache the response for future use
                    st.session_state.response_cache[user_input] = response
                    st.session_state.conversation_history.append({
                        'question': user_input,
                        'response': response
                    })
                except Exception as e:
                    st.error(f"ত্রুটি: {str(e)}")

    # Display conversation history
    if st.session_state.conversation_history:
        st.markdown("""
        <div class="chat-container">
            <div style="margin-top: 2rem; border-top: 1px solid %s; padding-top: 2rem;">
                <h3 style="font-size: 1.1rem; margin-bottom: 1.5rem;">Chat History</h3>
        """ % ('#3d424a' if st.session_state.dark_mode else '#e0e0e0'), 
        unsafe_allow_html=True)
        
        for chat in reversed(st.session_state.conversation_history):
            st.markdown(f"""
            <div class="user-message">{chat['question']}</div>
            <div class="bot-message">{chat['response']}</div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container

if __name__ == "__main__":
    main()