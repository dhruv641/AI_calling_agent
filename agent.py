
from transformers import pipeline

print("Loading sentiment analyzer...")
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
print("Sentiment analyzer loaded")
import os
import re
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


def lookup_customer(customer_id: str) -> str:
    """Look up customer information"""
    customer_data = {
        "CUST001": {
            "name": "John Smith",
            "account_balance": "$5,000",
            "last_purchase": "Oct 15, 2024",
            "status": "Premium Member"
        },
        "CUST002": {
            "name": "Sarah Johnson",
            "account_balance": "$2,500",
            "last_purchase": "Oct 10, 2024",
            "status": "Regular Member"
        }
    }
    
    if customer_id in customer_data:
        data = customer_data[customer_id]
        return f"Found customer: {data['name']}, Balance: {data['account_balance']}, Status: {data['status']}"
    else:
        return f"No customer found with ID: {customer_id}"


def check_appointment(customer_id: str) -> str:
    """Check appointments"""
    appointments = {
        "CUST001": "Nov 5, 2024 at 2:00 PM",
        "CUST002": None
    }
    
    if customer_id in appointments:
        apt = appointments[customer_id]
        if apt:
            return f"You have appointment scheduled: {apt}"
        else:
            return f"No appointment scheduled. Would you like to book one?"
    return "Could not find appointment data."


def schedule_appointment(customer_id: str, date: str, time: str) -> str:
    """Schedule appointment"""
    return f"✓ Appointment scheduled for customer {customer_id} on {date} at {time}"


def transfer_to_human(reason: str) -> str:
    """Transfer to human"""
    return f"[TRANSFERRING TO HUMAN AGENT] Reason: {reason}"



llm = Ollama(
    model="mistral",
    temperature=0.7,
    base_url="http://localhost:11434"
)


class ConversationManager:
    def __init__(self):
        self.messages = []
        self.customer_id = None
    
    def add_message(self, role: str, content: str):
        if role == "user":
            self.messages.append({"role": "user", "content": content})
        else:
            self.messages.append({"role": "assistant", "content": content})
    
    def get_context(self) -> str:
        context = "Conversation history:\n"
        for msg in self.messages:
            role = "Customer" if msg["role"] == "user" else "Agent"
            context += f"{role}: {msg['content']}\n"
        
        if self.customer_id:
            context += f"\nCurrent customer ID: {self.customer_id}\n"
        
        return context
    
    def extract_customer_id(self, text: str):
        match = re.search(r"CUST\d+", text)
        if match:
            self.customer_id = match.group(0)


def run_agent(user_input: str, conversation: ConversationManager, 
              call_logger=None, call_id: str = None) -> str:
    """
    SMART AGENT - Only uses tools when asked
    """
    
    # Analyze sentiment
    try:
        sentiment_result = sentiment_analyzer(user_input)
        sentiment = sentiment_result[0]["label"].lower()
        confidence = sentiment_result[0]["score"]
    except:
        sentiment = "neutral"
        confidence = 0.5
    
    print(f"  💭 Sentiment: {sentiment}")
    
    # Add to history
    conversation.add_message("user", user_input)
    conversation.extract_customer_id(user_input)
    
    # SMART PROMPT - Don't use tools unless asked
    system_prompt = """You are a customer service agent. 
Answer questions naturally. DON'T use tools unless explicitly asked.

Example:
- User: "Hi" → Respond: "Hello! How can I help you today?"
- User: "What's my balance?" → ONLY if you know customer ID, use lookup_customer
- User: "My ID is CUST001, what's my balance?" → THEN use lookup_customer(CUST001)

Tools available:
- lookup_customer(ID): Get customer info
- check_appointment(ID): Check appointments  
- schedule_appointment(ID, date, time): Schedule appointment
- transfer_to_human(reason): Transfer to human

IMPORTANT: Ask for customer ID first if you don't have it!"""
    
    full_prompt = f"""{system_prompt}

Customer ID we have: {conversation.customer_id if conversation.customer_id else "None - need to ask"}

Customer said: {user_input}

Respond naturally. Only use tools if the customer explicitly asks for something AND you have their ID."""
    
    # Get response
    response = llm.invoke(full_prompt)
    
    # Handle function calls ONLY if explicitly asked
    if "[FUNCTION_CALL:" in response:
        match = re.search(r'\[FUNCTION_CALL: (\w+)\(([^)]+)\)\]', response)
        if match:
            func_name = match.group(1)
            func_args = match.group(2)
            
            print(f"  → Calling: {func_name}")
            
            # Execute
            if func_name == "lookup_customer":
                args = func_args.strip().strip("'\"")
                result = lookup_customer(args)
            elif func_name == "check_appointment":
                args = func_args.strip().strip("'\"")
                result = check_appointment(args)
            elif func_name == "schedule_appointment":
                parts = [p.strip().strip("'\"") for p in func_args.split(",")]
                result = schedule_appointment(*parts)
            elif func_name == "transfer_to_human":
                result = "Connecting you to a human agent..."
            else:
                result = "Unknown function"
            
            # Log
            if call_logger and call_id:
                call_logger.log_tool_usage(call_id, func_name, func_args, result)
            
            # Short final response
            final_prompt = f"""Based on this tool result:
{result}

Give a brief, natural response to the customer."""
            
            response = llm.invoke(final_prompt)
    
    # Add to history
    conversation.add_message("assistant", response)
    
    # Log
    if call_logger and call_id:
        call_logger.add_message(call_id, user_input, response, sentiment)
    
    return response


if __name__ == "__main__":
    print("🤖 AI Agent Test - Text Mode")
    print("=" * 60)
    
    conversation = ConversationManager()
    
    test_inputs = [
        "Hi, I'm calling about my account. My ID is CUST001.",
        "Can you tell me my current balance?",
        "I'd like to schedule an appointment for Nov 20 at 3 PM.",
        "Thanks for your help!",
    ]
    
    for user_input in test_inputs:
        print(f"\n👤 Customer: {user_input}")
        print("-" * 60)
        
        response = run_agent(user_input, conversation)
        
        print(f"🤖 Agent: {response}")
        print()