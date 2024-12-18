from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import json
from .models import ChatSession, ChatMessage
from datetime import datetime, timedelta
from django.utils.timezone import now, make_aware, localtime
from pytz import timezone
from django.db.models.functions import TruncDate
from django.db.models import Count
import re
import os
from dotenv import load_dotenv

# Set Indian Standard Time
IST = timezone('Asia/Kolkata')

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is not set. Please check your .env file.")

openai.api_key = OPENAI_API_KEY

# Helper function to sanitize LaTeX for MathJax rendering
def sanitize_latex_response(response_text):
    """
    Preprocess OpenAI response for MathJax compatibility.
    Ensures equations are clean and wrapped for inline or block display.
    """
    # Remove unwanted spaces around LaTeX markers
    response_text = re.sub(r'\\\((.*?)\\\)', r'\\(\1\\)', response_text)  # Inline math
    response_text = re.sub(r'\\\[(.*?)\\\]', r'\\[\1\\]', response_text)  # Block math

    # Add line breaks before and after block equations for proper rendering
    response_text = re.sub(r'\\\[(.*?)\\\]', r'\n\\[\1\\]\n', response_text)

    # Trim extra spaces
    return response_text.strip()

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_message = data.get('message', '').strip()
            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)

            # Session Management
            today = now().astimezone(IST).date()
            session = ChatSession.objects.filter(created_at__date=today).first()
            if not session:
                session = ChatSession.objects.create(created_at=make_aware(datetime.now(), timezone=IST))

            # Structured Prompt
            structured_prompt = rf"""
You are an expert JEE tutor providing solutions and notes in a structured and professional format.

### Formatting Rules:
1. Use proper **Markdown syntax**:
   - **Headings in bold**: Use `**Heading Text**` for headings.
   - **Bullet points**: Use `- Point text` for bullet points.
   - Inline math: Use `\\( equation \\)` for equations.
   - Block math: Use:
     \\[
     equation
     \\]

2. **For problem-solving questions**:
   - **Given Data**: Clearly state the data provided.
   - **Solution Steps**: Number the steps and show each calculation.
   - **Final Answer**: Write the final answer clearly in bold.

3. **For notes or theory-based questions**:
   - Use bold headings for each section and bullet points for key points.
   - Conclude with a **Final Conclusion** in bold summarizing the topic.

Ensure your response strictly follows this structure and adheres to Markdown formatting for bold text, bullet points, and equations.

User Query: {user_message}
"""

            # OpenAI API Call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": structured_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5
            )

            bot_response = response['choices'][0]['message']['content'].strip()
            sanitized_response = sanitize_latex_response(bot_response)

            # Save to Database
            ChatMessage.objects.create(session=session, sender='user', message=user_message)
            ChatMessage.objects.create(session=session, sender='bot', message=sanitized_response)

            return JsonResponse({'response': sanitized_response}, status=200)

        except openai.error.OpenAIError as e:
            return JsonResponse({'error': 'Failed to fetch response from OpenAI API'}, status=500)
        except Exception as e:
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_chat_sessions(request):
    try:
        today = now().astimezone(IST).date()
        seven_days_ago = today - timedelta(days=7)

        sessions = (
            ChatSession.objects
            .filter(created_at__date__gte=seven_days_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('-date')
        )

        session_list = [{'date': session['date'].strftime('%Y-%m-%d')} for session in sessions]
        return JsonResponse({'sessions': session_list}, status=200)
    except Exception:
        return JsonResponse({'error': 'Unable to fetch chat sessions'}, status=500)


def get_session_messages_by_date(request, date):
    try:
        session_date = datetime.strptime(date, '%Y-%m-%d').date()
        messages = ChatMessage.objects.filter(session__created_at__date=session_date).order_by('created_at')

        message_list = [
            {
                'sender': message.sender,
                'message': message.message,
                'timestamp': localtime(message.created_at, IST).strftime('%Y-%m-%d %H:%M:%S'),
            }
            for message in messages
        ]
        return JsonResponse({'messages': message_list}, status=200)
    except Exception:
        return JsonResponse({'error': 'Unable to fetch messages for this date'}, status=500)

def chatbot_page(request):
    return render(request, 'chatbot.html')
