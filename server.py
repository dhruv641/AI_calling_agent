import os
from flask import Flask, jsonify, request
from agent_groq import run_agent
from gtts import gTTS
import tempfile

app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({"status": "✅ AI Calling Agent is LIVE!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/call', methods=['POST'])
def api_call():
    """API endpoint for handling calls"""
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        
        response = run_agent(user_input)
        
        return jsonify({
            "status": "success",
            "input": user_input,
            "response": response
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/incoming-call', methods=['POST'])
def incoming_call():
    """Jambonz webhook for incoming calls"""
    try:
        data = request.get_json()
        call_id = data.get('call_id')
        from_number = data.get('from')
        to_number = data.get('to')
        
        # Simple greeting
        agent_response = "Hello! This is an AI calling agent. How can I help you today?"
        
        # Convert to speech (TTS)
        tts = gTTS(text=agent_response, lang='en', slow=False)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts.save(f.name)
            audio_url = f"file://{f.name}"
        
        # Return Jambonz webhook response
        return jsonify({
            "say": agent_response,
            "action": "talk",
            "listen": True,
            "timeout": 10
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
