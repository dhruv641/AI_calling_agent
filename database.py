# database.py
"""
Database for storing call logs and transcripts.
Uses SQLite - free, no server needed.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Database file location
DB_PATH = Path("call_logs.db")

# ============================================
# CREATE DATABASE TABLES
# ============================================

def init_database():
    """Create database tables if they don't exist"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table 1: Call Records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            call_id TEXT PRIMARY KEY,
            customer_id TEXT,
            phone_number TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_seconds INTEGER,
            transcript TEXT,
            agent_response TEXT,
            sentiment TEXT,
            escalated INTEGER,
            tools_used TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    
    # Table 2: Performance Metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            total_calls INTEGER,
            avg_duration REAL,
            sentiment_positive INTEGER,
            sentiment_negative INTEGER,
            escalations INTEGER,
            tool_lookups INTEGER,
            tool_schedules INTEGER,
            created_at TEXT
        )
    """)
    
    # Table 3: Tools Usage Log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tool_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_id TEXT,
            tool_name TEXT,
            tool_input TEXT,
            tool_output TEXT,
            used_at TEXT,
            FOREIGN KEY(call_id) REFERENCES calls(call_id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized")


# ============================================
# CALL LOGGER CLASS
# ============================================

class CallLogger:
    """Handle all call logging operations"""
    
    def __init__(self):
        init_database()
    
    def start_call(self, call_id: str, customer_id: str = None, 
                   phone_number: str = None) -> dict:
        """
        Log the start of a call.
        
        Args:
            call_id: Unique call identifier
            customer_id: Customer identifier
            phone_number: Caller's phone number
        
        Returns:
            Call record
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        call_data = {
            "call_id": call_id,
            "customer_id": customer_id,
            "phone_number": phone_number,
            "start_time": datetime.now().isoformat(),
            "status": "active"
        }
        
        cursor.execute("""
            INSERT INTO calls (call_id, customer_id, phone_number, 
                             start_time, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (call_id, customer_id, phone_number, 
              call_data["start_time"], "active", datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"📞 Call started: {call_id}")
        return call_data
    
    def add_message(self, call_id: str, customer_message: str, 
                   agent_response: str, sentiment: str = "neutral"):
        """
        Log a message exchange in the call.
        
        Args:
            call_id: Which call this is from
            customer_message: What customer said
            agent_response: What agent responded
            sentiment: Sentiment of customer message
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Update call record with transcript
        cursor.execute("""
            UPDATE calls 
            SET transcript = COALESCE(transcript, '') || ?,
                sentiment = ?
            WHERE call_id = ?
        """, (f"\n[Customer]: {customer_message}\n[Agent]: {agent_response}",
              sentiment, call_id))
        
        conn.commit()
        conn.close()
    
    def log_tool_usage(self, call_id: str, tool_name: str, 
                      tool_input: str, tool_output: str):
        """
        Log when a tool is used during a call.
        
        Args:
            call_id: Which call
            tool_name: Name of tool (e.g., "lookup_customer")
            tool_input: What was passed to tool
            tool_output: What tool returned
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tool_usage (call_id, tool_name, tool_input, tool_output, used_at)
            VALUES (?, ?, ?, ?, ?)
        """, (call_id, tool_name, tool_input, tool_output, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"  📝 Logged tool: {tool_name}")
    
    def end_call(self, call_id: str, sentiment: str, escalated: bool = False):
        """
        Log the end of a call.
        
        Args:
            call_id: Which call ended
            sentiment: Overall sentiment of call
            escalated: Was it escalated to human?
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get call start time to calculate duration
        cursor.execute("SELECT start_time FROM calls WHERE call_id = ?", (call_id,))
        result = cursor.fetchone()
        
        if result:
            start_time = datetime.fromisoformat(result[0])
            duration = (datetime.now() - start_time).total_seconds()
        else:
            duration = 0
        
        # Update call with end info
        cursor.execute("""
            UPDATE calls 
            SET end_time = ?, duration_seconds = ?, 
                sentiment = ?, escalated = ?, status = ?
            WHERE call_id = ?
        """, (datetime.now().isoformat(), int(duration), 
              sentiment, 1 if escalated else 0, "completed", call_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Call ended: {call_id} (Duration: {duration:.1f}s)")
    
    def get_call_summary(self, call_id: str) -> dict:
        """Get summary of a specific call"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM calls WHERE call_id = ?", (call_id,))
        call = cursor.fetchone()
        
        conn.close()
        
        if call:
            return {
                "call_id": call[0],
                "customer_id": call[1],
                "duration": call[6],
                "sentiment": call[9],
                "escalated": call[10],
                "status": call[11]
            }
        return None
    
    def get_metrics(self) -> dict:
        """Get overall system metrics"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count calls
        cursor.execute("SELECT COUNT(*) FROM calls WHERE status = 'completed'")
        total_calls = cursor.fetchone()[0]
        
        # Average duration
        cursor.execute("""
            SELECT AVG(duration_seconds) FROM calls 
            WHERE status = 'completed'
        """)
        avg_duration = cursor.fetchone()[0] or 0
        
        # Sentiment breakdown
        cursor.execute("""
            SELECT sentiment, COUNT(*) FROM calls 
            WHERE status = 'completed' GROUP BY sentiment
        """)
        sentiment_data = cursor.fetchall()
        
        # Escalations
        cursor.execute("""
            SELECT COUNT(*) FROM calls 
            WHERE escalated = 1 AND status = 'completed'
        """)
        escalations = cursor.fetchone()[0]
        
        # Tool usage
        cursor.execute("""
            SELECT tool_name, COUNT(*) FROM tool_usage 
            GROUP BY tool_name
        """)
        tool_usage = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_calls": total_calls,
            "avg_duration": round(avg_duration, 1),
            "sentiment": dict(sentiment_data),
            "escalations": escalations,
            "tool_usage": tool_usage
        }


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    logger = CallLogger()
    
    # Test logging
    logger.start_call("CALL001", "CUST001", "+1-555-123-4567")
    logger.add_message("CALL001", "Hi, what's my balance?", 
                      "Your balance is $5000", "positive")
    logger.log_tool_usage("CALL001", "lookup_customer", "CUST001", 
                         "John Smith, $5000")
    logger.end_call("CALL001", "positive", escalated=False)
    
    # Get metrics
    metrics = logger.get_metrics()
    print("\n📊 Metrics:")
    print(json.dumps(metrics, indent=2))