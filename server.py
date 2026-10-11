# server.py
"""
FastAPI server for phone integration.
This will receive calls from Jambonz and route to your agent.
"""

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse
import json
import uuid
from agent import ConversationManager, run_agent
from database import CallLogger
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Store active calls
ACTIVE_CALLS = {}

# Initialize logger
call_logger = CallLogger()

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/")
async def health_check():
    """Just to verify server is running"""
    return {"status": "✅ AI Calling Agent is LIVE!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ============================================
# INCOMING CALL HANDLER (For Jambonz)
# ============================================

@app.post("/incoming-call")
async def incoming_call(request: Request):
    """
    When someone calls your number, this receives the webhook.
    Jambonz sends: call_id, caller_number, etc.
    """
    
    try:
        data = await request.json()
        
        call_id = str(uuid.uuid4())[:8].upper()
        caller_number = data.get("from", "unknown")
        
        print(f"📞 Incoming call from {caller_number}")
        
        # Log call start
        call_logger.start_call(call_id, phone_number=caller_number)
        
        # Create conversation for this call
        conversation = ConversationManager()
        ACTIVE_CALLS[call_id] = {
            "conversation": conversation,
            "caller": caller_number,
            "started": True
        }
        
        # Send TwiML response (tells Jambonz what to do)
        response = {
            "status": "success",
            "call_id": call_id,
            "message": "Call connected to AI agent"
        }
        
        return JSONResponse(response)
    
    except Exception as e:
        print(f"❌ Error in incoming call: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# ============================================
# MESSAGE HANDLER (Customer sends text/voice)
# ============================================

@app.post("/message")
async def handle_message(request: Request):
    """
    When customer says something, this processes it.
    
    Expected payload:
    {
        "call_id": "ABC123",
        "message": "What's my balance?"  # or speech transcribed
    }
    """
    
    try:
        data = await request.json()
        
        call_id = data.get("call_id")
        user_message = data.get("message", "").strip()
        
        if not call_id or call_id not in ACTIVE_CALLS:
            return JSONResponse({"error": "Call not found"}, status_code=404)
        
        if not user_message:
            return JSONResponse({"error": "No message"}, status_code=400)
        
        # Get conversation
        conversation = ACTIVE_CALLS[call_id]["conversation"]
        
        print(f"📨 Message from {call_id}: {user_message}")
        
        # Process with agent
        agent_response = run_agent(user_message, conversation, call_logger, call_id)
        
        print(f"🤖 Response: {agent_response}")
        
        return JSONResponse({
            "status": "success",
            "response": agent_response,
            "call_id": call_id
        })
    
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# ============================================
# CALL END HANDLER
# ============================================

@app.post("/call-ended")
async def call_ended(request: Request):
    """
    When call ends, log it and clean up.
    """
    
    try:
        data = await request.json()
        call_id = data.get("call_id")
        
        if call_id and call_id in ACTIVE_CALLS:
            # Log call end
            call_logger.end_call(call_id, "neutral", escalated=False)
            
            # Clean up
            del ACTIVE_CALLS[call_id]
            
            print(f"✅ Call ended: {call_id}")
        
        return JSONResponse({"status": "success"})
    
    except Exception as e:
        print(f"❌ Error ending call: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# ============================================
# METRICS ENDPOINT
# ============================================

@app.get("/metrics")
async def get_metrics():
    """Get system metrics for monitoring"""
    
    metrics = call_logger.get_metrics()
    
    return {
        "status": "healthy",
        "total_calls": metrics["total_calls"],
        "avg_duration": metrics["avg_duration"],
        "sentiment": metrics["sentiment"],
        "escalations": metrics["escalations"],
        "tools_used": metrics["tool_usage"]
    }

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    # Run on port 8000
    # For production: uvicorn server:app --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)