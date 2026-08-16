import os
import sys
from dotenv import load_dotenv

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.state import AgentState
from agents.graph import build_graph
from utils.tools import write_file, get_file_path

# Load environment variables
load_dotenv()

# Check for Groq API key
if not os.getenv("GROQ_API_KEY"):
    print("❌ ERROR: GROQ_API_KEY not found in .env file!")
    print("Get your free key from: https://console.groq.com/keys")
    exit(1)

def main():
    print("🚀 Starting SWE Agent Lite (Groq Edition)...\n")
    
    initial_state = {
        "issue": "The divide function crashes when denominator is 0. Fix it to return 'Error: Division by zero' instead of crashing.",
        "file_content": "",
        "file_path": "",
        "proposed_patch": "",
        "score": 0.0,
        "feedback": "",
        "iteration": 0,
        "history": []
    }
    
    try:
        app = build_graph()
        print("⚙️ Running the agent workflow...\n")
        final_state = app.invoke(initial_state)
        
        print("\n" + "="*50)
        print("📦 FINAL RESULTS")
        print("="*50)
        print(f"✅ Issue: {final_state['issue']}")
        print(f"📊 Final Score: {final_state['score']}")
        print(f"💬 Final Feedback: {final_state['feedback']}")
        print(f"🔄 Total Iterations: {final_state['iteration']}")
        
        if final_state.get('proposed_patch'):
            file_path = final_state.get('file_path', get_file_path("buggy_script.py"))
            write_file(file_path, final_state['proposed_patch'])
            print(f"📝 Patch written to: {file_path}")
        
        print("\n📜 History:")
        for entry in final_state.get('history', []):
            print(f"  - {entry}")
        
        print("\n✅ Agent finished successfully!")
        
    except Exception as e:
        print(f"\n❌ Agent failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()