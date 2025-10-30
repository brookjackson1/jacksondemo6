from flask import Blueprint, render_template, request, jsonify
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

chat_bp = Blueprint('chat', __name__)

def get_groq_response(question):
    """
    Generate AI response using Groq API
    """
    try:
        # Initialize Groq client
        api_key = os.environ.get('GROQ_API_KEY')
        print(f"[DEBUG] API Key present: {bool(api_key)}")

        client = Groq(api_key=api_key)
        print(f"[DEBUG] Groq client initialized")

        # Create chat completion
        print(f"[DEBUG] Sending question: {question[:50]}...")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model="llama-3.3-70b-versatile",  # Current supported model
        )

        response = chat_completion.choices[0].message.content
        print(f"[DEBUG] Got response: {response[:100]}...")
        return response

    except Exception as e:
        print(f"[ERROR] Groq API error: {e}")
        import traceback
        traceback.print_exc()
        return None


@chat_bp.route('/chatbot', methods=['GET'])
def index():
    """Display chat interface"""
    return render_template("chat.html", response=None)


@chat_bp.route('/chatbot/ask', methods=['POST'])
def ask():
    """Handle chat questions via POST form"""
    question = request.form.get('question', '').strip()

    if not question:
        return render_template("chat.html",
                             response=None,
                             error="Question is required")

    # Check if API key is configured
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return render_template("chat.html",
                             response=None,
                             error="Groq API key is not configured. Please set GROQ_API_KEY in environment variables.")

    # Get response from Groq
    response = get_groq_response(question)

    if response is None:
        return render_template("chat.html",
                             response=None,
                             error="Failed to get response from Groq API. Please try again.")

    return render_template("chat.html",
                         response=response,
                         question=question)
