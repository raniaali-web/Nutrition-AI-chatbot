import json
import re
from datetime import datetime
import streamlit as st

def format_nutrition_response(text):
    """
    Format nutrition responses with emojis, bullet points, and better readability
    """
    if not text:
        return text
    
    # Add emojis for common nutrition terms
    emoji_map = {
        r'(?i)protein': '💪 protein',
        r'(?i)vitamin': '💊 vitamin',
        r'(?i)water|hydrat': '💧 water',
        r'(?i)vegetable|veggie': '🥬 vegetable',
        r'(?i)fruit': '🍎 fruit',
        r'(?i)breakfast': '🍳 breakfast',
        r'(?i)lunch': '🥪 lunch',
        r'(?i)dinner': '🍽️ dinner',
        r'(?i)snack': '🍿 snack',
        r'(?i)exercise|workout': '🏋️ exercise',
        r'(?i)sleep': '😴 sleep',
        r'(?i)sugar': '🍬 sugar',
        r'(?i)fat|oil': '🫒 fat',
        r'(?i)carb|carbohydrate': '🍚 carbs',
        r'(?i)fiber': '🌾 fiber',
        r'(?i)calcium': '🥛 calcium',
        r'(?i)iron': '🩸 iron',
        r'(?i)warning|caution': '⚠️ warning',
        r'(?i)healthy': '✅ healthy',
    }
    
    formatted_text = text
    for pattern, emoji_word in emoji_map.items():
        formatted_text = re.sub(pattern, emoji_word, formatted_text, flags=re.IGNORECASE)
    
    # Ensure bullet points are properly formatted
    lines = formatted_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Convert markdown bullet points (* or -) to HTML-like bullet points
        if re.match(r'^\s*[\*\-]\s+', line):
            line = '• ' + line.lstrip('*- ').strip()
        # Convert numbered lists
        elif re.match(r'^\s*\d+\.\s+', line):
            line = line  # Keep as is
        formatted_lines.append(line)
    
    formatted_text = '\n'.join(formatted_lines)
    
    # Add extra spacing after bullet points
    formatted_text = re.sub(r'(•[^\n]+\n)', r'\1\n', formatted_text)
    
    return formatted_text

def extract_keywords(query):
    """
    Extract nutrition-related keywords from user query for context
    """
    nutrition_keywords = [
        'calorie', 'protein', 'fat', 'carb', 'sugar', 'fiber', 'vitamin', 
        'mineral', 'water', 'hydrate', 'diet', 'meal', 'breakfast', 'lunch',
        'dinner', 'snack', 'exercise', 'workout', 'weight', 'lose', 'gain',
        'healthy', 'organic', 'vegan', 'vegetarian', 'keto', 'paleo', 
        'mediterranean', 'gluten', 'dairy', 'allergy', 'intolerance',
        'immune', 'energy', 'sleep', 'stress', 'digestion', 'gut'
    ]
    
    query_lower = query.lower()
    found_keywords = [kw for kw in nutrition_keywords if kw in query_lower]
    
    return found_keywords

def save_chat_history(messages, filename="chat_history.json"):
    """
    Save chat history to JSON file
    """
    try:
        # Prepare messages for saving (remove any non-serializable objects)
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "total_questions": st.session_state.get("total_questions", 0),
            "total_answers": st.session_state.get("total_answers", 0)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving chat history: {e}")
        return False

def load_chat_history(filename="chat_history.json"):
    """
    Load chat history from JSON file
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            messages = data.get("messages", [])
            
            # Restore session state counters if they exist
            if "total_questions" in data and hasattr(st, 'session_state'):
                st.session_state.total_questions = data["total_questions"]
                st.session_state.total_answers = data["total_answers"]
            
            return messages
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading chat history: {e}")
        return []

def validate_nutrition_query(query):
    """
    Basic validation to ensure query is nutrition-related
    """
    nutrition_indicators = [
        'food', 'eat', 'diet', 'nutrition', 'health', 'meal', 'recipe',
        'calorie', 'protein', 'vitamin', 'mineral', 'weight', 'exercise',
        'workout', 'sleep', 'water', 'hydrate', 'cook', 'ingredient'
    ]
    
    query_lower = query.lower()
    is_relevant = any(indicator in query_lower for indicator in nutrition_indicators)
    
    if not is_relevant and len(query.split()) > 3:
        return False, "⚠️ Please ask nutrition or health-related questions for best results."
    
    return True, None