import streamlit as st
import time
from datetime import datetime
from groq import Groq
import os
from dotenv import load_dotenv
from utils import format_nutrition_response, extract_keywords, save_chat_history, load_chat_history

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Nutrition AI Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for nutrition theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 100%);
    }
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #4caf50, #2e7d32);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .nutrition-card {
        background-color: white;
        border-left: 5px solid #4caf50;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        font-size: 0.8rem;
        color: #666;
        margin-top: 2rem;
    }
    .stat-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stButton > button {
        background-color: #4caf50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #2e7d32;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Groq client
@st.cache_resource
def init_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ GROQ_API_KEY not found in .env file. Please add your API key.")
        st.stop()
    return Groq(api_key=api_key)

# Initialize session state
if "messages" not in st.session_state:
    # Load chat history if exists
    loaded_messages = load_chat_history()
    if loaded_messages:
        st.session_state.messages = loaded_messages
    else:
        st.session_state.messages = []
    
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0
if "total_answers" not in st.session_state:
    st.session_state.total_answers = 0

# System prompt for nutritionist AI
SYSTEM_PROMPT = """You are a certified nutritionist and health expert. Follow these guidelines strictly:

1. Provide science-based, evidence-backed nutritional advice
2. Use bullet points (•) for easy reading
3. Include relevant emojis (🥗, 🍎, 💧, ⚠️, ✅) to make responses engaging
4. Always include a disclaimer: "⚠️ Consult a healthcare provider before making significant dietary changes"
5. Be practical and actionable - give specific food examples and portion sizes
6. Address common myths with scientific facts
7. Encourage balanced, sustainable eating habits
8. Never promote extreme diets or supplements without medical supervision
9. For medical conditions, always recommend consulting a doctor
10. Focus on whole foods, hydration, and mindful eating

Remember: You are not a medical doctor. Always defer to physicians for diagnosis and treatment of medical conditions."""

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/nutritionist.png", width=80)
    st.title("🥗 Nutrition AI")
    st.markdown("---")
    
    # Model selection - UPDATED with current models
    st.subheader("🤖 Model Settings")
    selected_model = st.selectbox(
        "Choose AI Model",
        options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0,
        help="llama-3.3-70b: Most capable | llama-3.1-8b: Fastest | mixtral: Balanced"
    )
    
    temperature = st.slider(
        "Temperature (Creativity)",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Lower = more focused, Higher = more creative responses"
    )
    
    st.markdown("---")
    
    # Example questions
    st.subheader("💡 Example Questions")
    example_questions = [
        "What are the best sources of plant-based protein? 🌱",
        "How can I reduce sugar cravings naturally? 🍬",
        "What should I eat before and after a workout? 💪",
        "Tips for staying hydrated throughout the day? 💧",
        "Foods that boost immune system? 🛡️",
        "Healthy breakfast ideas for weight management? 🥣"
    ]
    
    for q in example_questions:
        if st.button(q, key=f"example_{q[:20]}"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.session_state.total_questions += 1
            st.rerun()
    
    st.markdown("---")
    
    # Chat Statistics
    st.subheader("📊 Chat Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h3>❓ {st.session_state.total_questions}</h3>
            <p>Questions</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h3>💬 {st.session_state.total_answers}</h3>
            <p>Answers</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.total_questions > 0:
        ratio = st.session_state.total_answers / st.session_state.total_questions
        st.metric("Response Ratio", f"{ratio:.1f}x", help="Average responses per question")
    
    st.markdown("---")
    
    # Action buttons
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_questions = 0
        st.session_state.total_answers = 0
        save_chat_history([])
        st.rerun()
    
    if st.button("💾 Save Chat", use_container_width=True):
        save_chat_history(st.session_state.messages)
        st.success("Chat saved successfully!")
    
    st.markdown("---")
    st.caption("Powered by Groq API 🚀")

# Main content
st.markdown("""
<div class="main-header">
    <h1>🥗 Your Personal Nutrition Assistant</h1>
    <p>Science-based nutrition advice at your fingertips</p>
</div>
""", unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            # Format assistant responses with emojis and bullet points
            formatted_content = format_nutrition_response(message["content"])
            st.markdown(formatted_content)
        else:
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about nutrition and health..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.total_questions += 1
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Extract keywords for context
    keywords = extract_keywords(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Measure response time
        start_time = time.time()
        
        try:
            client = init_groq_client()
            
            # Prepare messages for API
            api_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *st.session_state.messages
            ]
            
            # Make API call
            stream = client.chat.completions.create(
                model=selected_model,
                messages=api_messages,
                temperature=temperature,
                max_tokens=1000,
                stream=True
            )
            
            # Stream response
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    # Format on the fly
                    formatted_response = format_nutrition_response(full_response)
                    message_placeholder.markdown(formatted_response + "▌")
            
            # Final formatted response
            final_formatted = format_nutrition_response(full_response)
            message_placeholder.markdown(final_formatted)
            
            # Calculate response time
            end_time = time.time()
            response_time = end_time - start_time
            
            # Add response time indicator
            st.caption(f"⏱️ Response time: {response_time:.2f} seconds")
            
            # Add to session state
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.total_answers += 1
            
            # Save chat history
            save_chat_history(st.session_state.messages)
            
        except Exception as e:
            error_message = f"❌ **API Error**: {str(e)}\n\nPlease check your API key or try again later."
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# Footer
st.markdown("""
<div class="footer">
    <p>⚠️ <strong>Medical Disclaimer:</strong> This AI assistant provides general nutritional information only. 
    It is not a substitute for professional medical advice, diagnosis, or treatment. 
    Always consult a qualified healthcare provider before making changes to your diet or health routine.</p>
    <p>🍎 Eat whole foods • 💧 Stay hydrated • 🏃‍♂️ Exercise regularly • 😴 Get adequate sleep</p>
    <p>Made with ❤️ using Groq API • Data is not saved permanently</p>
</div>
""", unsafe_allow_html=True)