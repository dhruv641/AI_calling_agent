# call_simulator.py
"""
Simulate a phone call locally.
Text in → Agent processes → Text out → Speak

This is what will happen on a REAL call,
but we're testing locally first.
"""

from agent import ConversationManager, run_agent
from speech import SpeechToText, TextToSpeech
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# SIMULATE A PHONE CALL
# ============================================

class CallSimulator:
    """
    Simulates a complete phone call.
    
    FLOW:
    1. User speaks (or we simulate with text)
    2. Convert speech → text
    3. Agent processes
    4. Convert response → speech
    5. Play to user
    """
    
    def __init__(self, simulate_speech=True):
        """
        Initialize call simulator.
        
        Args:
            simulate_speech: If True, use text input (no mic needed)
                            If False, record from mic
        """
        print("Initializing call simulator...")
        
        self.conversation = ConversationManager()
        self.tts = TextToSpeech()
        self.stt = SpeechToText(model_size="base")
        self.simulate_speech = simulate_speech
        
        print("✅ Call simulator ready\n")
    
    def simulate_call(self, test_inputs=None):
        """
        Simulate a complete call with test inputs.
        
        Args:
            test_inputs: List of customer messages to simulate
        """
        if test_inputs is None:
            test_inputs = [
                "Hi, I'm customer CUST001. What's my balance?",
                "Can I schedule an appointment?",
                "I'd like Nov 20 at 3 PM please",
                "Thank you!",
            ]
        
        print("📞 SIMULATED CALL STARTING")
        print("=" * 60)
        
        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n[Call Step {i}]")
            print("-" * 60)
            
            # Step 1: Customer speaks (simulated as text)
            print(f"🎤 Customer: {user_input}")
            
            # Step 2: Agent processes
            print(f"🤖 Agent thinking...")
            agent_response = run_agent(user_input, self.conversation)
            
            # Step 3: Agent speaks (text to speech)
            print(f"🔊 Agent: {agent_response}")
            
            # Generate audio (but don't play to avoid interruptions during testing)
            self.tts.synthesize(agent_response, f"output_{i}.mp3")
            print(f"   [Audio saved to output_{i}.mp3]")
            
            print()
    
    def interactive_call(self):
        """
        Interactive call - you type in customer messages.
        """
        print("📞 INTERACTIVE CALL")
        print("=" * 60)
        print("Type customer messages (type 'bye' to end call)\n")
        
        while True:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() == "bye":
                print("\n🤖 Agent: Thank you for calling. Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process through agent
            agent_response = run_agent(user_input, self.conversation)
            print(f"🤖 Agent: {agent_response}\n")


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    # Start call simulator
    simulator = CallSimulator(simulate_speech=True)
    
    # Option 1: Run simulated call with pre-set inputs
    print("Running SIMULATED call with test inputs...")
    simulator.simulate_call()
    
    # Option 2: Uncomment to run interactive call (you type inputs)
    # print("\nStarting INTERACTIVE call...")
    # simulator.interactive_call()