import os
from flask import Flask, jsonify, request
from agent_groq import run_agent

app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({"status": "✅ AI Calling Agent is LIVE!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/metrics')
def metrics():
    return jsonify({"status": "healthy", "calls": 0})

@app.route('/api/call', methods=['POST'])
def api_call():
    """Main API endpoint for handling calls"""
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
