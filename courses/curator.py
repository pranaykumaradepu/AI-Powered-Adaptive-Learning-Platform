import os
import json
import google.generativeai as genai
from tavily import TavilyClient

# 1. CONFIGURE API CLIENTS
# Ensure these keys are in your .env file!
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

# 2. CONFIGURATION
TRUSTED_DOMAINS = [
    "freecodecamp.org", "dev.to", "github.com", 
    "react.dev", "docs.python.org", "youtube.com"
]

# Use the latest stable model
MODEL_NAME = 'gemini-2.5-flash' # Or 'gemini-pro'

# ==========================================
# FUNCTION 1: SEARCH & CREATE COURSE (Phase 2)
# ==========================================
# courses/curator.py

def generate_course_plan(topic, goal, level="Beginner", duration="Short"):
    print(f"🧠 AI Thinking: Generating deep content for {topic}...")
    
    model = genai.GenerativeModel(MODEL_NAME)
    
    # NEW: We ask for "content" (long explanation) and "video_query"
    prompt = f"""
    Create a structured learning path for:
    - Topic: {topic}
    - Goal: {goal}
    - Level: {level} ({duration})
    
    For each module, write a "mini-lesson" that actually teaches the concept.
    
    Return VALID JSON:
    {{
        "course_title": "Title",
        "modules": [
            {{
                "order": 1,
                "title": "Module Title",
                "content": "## Core Concept\\nExplain the concept clearly here.\\n\\n## Example\\nProvide a real-world example.\\n\\n## Code\\n```python\\nprint('Show code examples')\\n```",
                "video_query": "python {topic} tutorial beginner",
                "is_project": false
            }}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return None

# ==========================================
# FUNCTION 2: GENERATE QUIZ 
# ==========================================
def generate_quiz_questions(module_title, context_text):
    print(f"🧠 Generating quiz for: {module_title}")
    
    model = genai.GenerativeModel(MODEL_NAME)
    
    prompt = f"""
    Create 3 multiple-choice questions to test a student on this topic: "{module_title}".
    Context: {context_text}
    
    Return ONLY valid JSON array:
    [
        {{
            "question": "Question text here?",
            "a": "Option A text",
            "b": "Option B text",
            "c": "Option C text",
            "answer": "A" 
        }}
    ]
    """
    
    try:
        response = model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Quiz Generation Error: {e}")
        return []

# ==========================================
# FUNCTION 3: GRADE CODE PROJECT 
# ==========================================
def grade_code_submission(module_title, user_code):
    """
    Analyzes code snippets for Project-Based Validation.
    """
    print(f"💻 Grading code for: {module_title}")
    model = genai.GenerativeModel(MODEL_NAME)
    
    prompt = f"""
    You are a Senior Developer. 
    Task: Review this code submission for the module "{module_title}".
    
    User Code:
    {user_code}
    
    Analyze strictly:
    1. Does it solve the core problem of {module_title}?
    2. Is the syntax correct?
    
    Return JSON:
    {{
        "score": 85, 
        "feedback": "Good logic, but you missed..."
    }}
    """
    try:
        response = model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Grading Error: {e}")
        return {"score": 0, "feedback": "AI Error: Could not grade code."}

# ==========================================
# FUNCTION 4: MICRO-LESSON 
# ==========================================
def generate_micro_lesson(module_title, weak_topic):
    """
    Creates a remedial lesson for the 'Soft Pass' scenario.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"The student understands '{module_title}' generally but is weak in '{weak_topic}'. Write a 100-word 'Micro-Lesson' to fix this specific gap."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Review the previous module's resources."