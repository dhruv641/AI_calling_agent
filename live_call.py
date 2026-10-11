# live_call.py (UPDATED)
"""
LIVE CALLING SIMULATOR with logging & sentiment analysis
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from agent import ConversationManager, run_agent
from database import CallLogger
from gtts import gTTS
import tempfile
import os
import whisper
import uuid
from datetime import datetime

class LiveCallSimulator:
    def __init__(self):
        print("🚀 Initializing Live Call Simulator...")
        
        print("Loading Whisper model...")
        self.stt = whisper.load_model("base")
        print("✅ Whisper loaded")
        
        self.conversation = ConversationManager()
        self.call_logger = CallLogger()
        print("✅ Agent ready\n")
    
    def record_audio(self, duration: int = 5, sample_rate: int = 16000):
        print(f"🎤 Recording for {duration} seconds... Speak now!\n")
        
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        return audio, sample_rate
    
    def transcribe_audio(self, audio: np.ndarray, sample_rate: int) -> str:
        print("🔄 Transcribing your speech...")
        
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(temp_file.name, audio, sample_rate)
        
        result = self.stt.transcribe(temp_file.name, language="en")
        text = result["text"].strip()
        
        os.unlink(temp_file.name)
        
        return text
    
    def speak_response(self, text: str):
        print("🔊 Generating speech...")
        
        try:
            tts = gTTS(text, lang='en', slow=False)
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tts.save(temp_file.name)
            
            os.system(f"afplay {temp_file.name}")
            os.unlink(temp_file.name)
        
        except Exception as e:
            print(f"⚠️ Could not play audio: {e}")
    
    def run_live_call(self):
        # Generate unique call ID
        call_id = f"CALL_{uuid.uuid4().hex[:8].upper()}"
        
        print("=" * 70)
        print("📞 LIVE CALLING SIMULATOR STARTED")
        print(f"Call ID: {call_id}")
        print("=" * 70)
        
        # Log call start
        self.call_logger.start_call(call_id)
        
        call_counter = 1
        
        while True:
            print(f"\n[Exchange {call_counter}]")
            print("-" * 70)
            
            audio, sample_rate = self.record_audio(duration=5)
            user_text = self.transcribe_audio(audio, sample_rate)
            print(f"👤 You said: {user_text}\n")
            
            if user_text.lower() in ["quit", "bye", "goodbye", "exit"]:
                print("🤖 Agent: Thank you for calling! Goodbye!")
                # Log call end
                self.call_logger.end_call(call_id, "neutral", escalated=False)
                break
            
            print("🤖 Agent thinking...")
            # Pass call_id and logger to agent
            agent_response = run_agent(user_text, self.conversation, 
                                      self.call_logger, call_id)
            print(f"🤖 Agent response: {agent_response}\n")
            
            print("🔊 Agent speaking...")
            self.speak_response(agent_response)
            print("✅ Response played\n")
            
            call_counter += 1
        
        # Show call summary
        summary = self.call_logger.get_call_summary(call_id)
        print("\n" + "=" * 70)
        print("📞 CALL ENDED")
        print(f"📊 Duration: {summary['duration']}s")
        print(f"💭 Overall Sentiment: {summary['sentiment']}")
        print(f"🔄 Escalated: {'Yes' if summary['escalated'] else 'No'}")
        print("=" * 70)
        
        # Show metrics
        metrics = self.call_logger.get_metrics()
        print("\n📊 OVERALL METRICS:")
        print(f"  Total Calls: {metrics['total_calls']}")
        print(f"  Avg Duration: {metrics['avg_duration']}s")
        print(f"  Escalations: {metrics['escalations']}")
        print(f"  Tools Used: {metrics['tool_usage']}")


if __name__ == "__main__":
    simulator = LiveCallSimulator()
    simulator.run_live_call()