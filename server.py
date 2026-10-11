import os
from flask import Flask, jsonify

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
