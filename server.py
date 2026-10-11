from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "✅ AI Calling Agent is LIVE!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/incoming-call")
async def incoming_call(request: Request):
    try:
        data = await request.json()
        return JSONResponse({"status": "success", "message": "Call received"})
    except:
        return JSONResponse({"status": "error"}, status_code=500)

@app.get("/metrics")
async def metrics():
    return {"status": "healthy", "calls": 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)