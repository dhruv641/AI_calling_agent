import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "mock")

def run_agent(user_input: str) -> str:
    """Run agent with Groq API (or mock if key invalid)"""
    
    # If no real key, return mock response
    if GROQ_API_KEY == "mock" or not GROQ_API_KEY:
        mock_responses = {
            "hello": "Hello! I'm an AI calling agent. How can I help you today?",
            "2+2": "2 + 2 equals 4.",
            "who are you": "I'm an AI calling agent built with LangChain and Groq.",
        }
        
        for key, response in mock_responses.items():
            if key.lower() in user_input.lower():
                return response
        
        return f"You said: '{user_input}'. I'm ready to help with calls!"
    
    # Real Groq API call
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "You are a helpful AI calling agent."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            # If Groq fails, return mock
            return f"[Using mock response] You asked: {user_input}"
    except:
        return f"[Using mock response] You asked: {user_input}"
