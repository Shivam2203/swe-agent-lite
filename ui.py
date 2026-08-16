import streamlit as st
import requests
import json
import time

# Page configuration
st.set_page_config(
    page_title="🤖 SWE Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🤖 SWE Agent Lite</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Multi-Agent Bug Fixer with HyDE + VectorDB</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_url = st.text_input(
        "API URL",
        value="http://localhost:8000",
        help="URL of the FastAPI backend"
    )
    
    st.divider()
    
    st.header("📊 Stats")
    
    if 'stats' not in st.session_state:
        st.session_state.stats = {
            'total_fixes': 0,
            'successful_fixes': 0,
            'average_score': 0.0
        }
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Fixes", st.session_state.stats['total_fixes'])
    with col2:
        st.metric("Success Rate", 
                  f"{st.session_state.stats['successful_fixes']/st.session_state.stats['total_fixes']*100:.0f}%" 
                  if st.session_state.stats['total_fixes'] > 0 else "N/A")
    
    st.divider()
    
    st.header("📖 Examples")
    examples = [
        "Fix division by zero",
        "Handle missing dictionary key",
        "Add try-except for file operations",
        "Fix list index out of range"
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.issue = ex
            st.rerun()

# Main content
tab1, tab2, tab3 = st.tabs(["🐛 Fix Bug", "📊 Results", "📈 History"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Describe the Bug")
        
        # Issue description
        issue = st.text_area(
            "What's the bug?",
            value=st.session_state.get('issue', 'The divide function crashes when denominator is 0. Fix it to return "Error: Division by zero" instead of crashing.'),
            height=100,
            placeholder="Describe the bug in detail..."
        )
        
        # Code input
        st.subheader("💻 Code to Fix")
        code = st.text_area(
            "Paste your buggy code here",
            value="""
def divide(a, b):
    # BUG: This crashes if b == 0
    return a / b

def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(divide(10, 2))
    print(divide(10, 0))  # CRASHES!
""",
            height=200,
            placeholder="Paste your code here..."
        )
        
        # Max iterations
        max_iterations = st.slider("Max Iterations", 1, 5, 3)
    
    with col2:
        st.subheader("🎯 Settings")
        
        use_api = st.checkbox("Use API (vs local)", value=False)
        
        st.markdown("---")
        st.caption("💡 Tip: You can also use the sidebar for quick examples.")
        
        st.markdown("---")
        st.caption("🔬 Powered by:")
        st.caption("- Groq Llama 3.3 70B")
        st.caption("- ChromaDB Vector Store")
        st.caption("- HyDE Search")
        st.caption("- LangGraph Multi-Agent")
    
    # Fix button
    if st.button("🚀 Fix Bug", type="primary", use_container_width=True):
        if not issue or not code:
            st.error("Please provide both issue description and code.")
        else:
            with st.spinner("🤖 Agent is analyzing and fixing the bug..."):
                try:
                    if use_api:
                        # Use API
                        response = requests.post(
                            f"{api_url}/fix-bug",
                            json={
                                "issue": issue,
                                "code": code,
                                "max_iterations": max_iterations
                            },
                            timeout=60
                        )
                        if response.status_code == 200:
                            result = response.json()
                        else:
                            st.error(f"API Error: {response.status_code}")
                            st.stop()
                    else:
                        # Use local agent
                        import sys
                        import tempfile
                        sys.path.insert(0, 'src')
                        from agents.graph import build_graph
                        
                        initial_state = {
                            "issue": issue,
                            "file_content": code,
                            "file_path": "",
                            "proposed_patch": "",
                            "score": 0.0,
                            "feedback": "",
                            "iteration": 0,
                            "history": []
                        }
                        
                        agent = build_graph()
                        final_state = agent.invoke(initial_state)
                        
                        result = {
                            "success": final_state['score'] >= 0.8,
                            "score": final_state['score'],
                            "iterations": final_state['iteration'],
                            "feedback": final_state['feedback'],
                            "fixed_code": final_state.get('proposed_patch', code)
                        }
                    
                    # Store result in session
                    st.session_state.last_result = result
                    st.session_state.stats['total_fixes'] += 1
                    if result['success']:
                        st.session_state.stats['successful_fixes'] += 1
                    
                    # Save to history
                    if 'history' not in st.session_state:
                        st.session_state.history = []
                    st.session_state.history.append({
                        'timestamp': time.time(),
                        'issue': issue,
                        'score': result['score'],
                        'success': result['success']
                    })
                    
                    st.success("✅ Bug fixed successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab2:
    if 'last_result' in st.session_state:
        result = st.session_state.last_result
        
        st.subheader("📊 Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{result['score']:.2f}")
        with col2:
            st.metric("Iterations", result['iterations'])
        with col3:
            status = "✅ Success" if result['success'] else "❌ Failed"
            st.metric("Status", status)
        
        st.subheader("💬 Feedback")
        st.info(result['feedback'])
        
        st.subheader("📝 Fixed Code")
        st.code(result['fixed_code'], language="python")
        
        # Diff view (simplified)
        if 'fixed_code' in result and result['fixed_code']:
            st.subheader("🔍 Changes")
            st.caption("The agent has generated a fixed version of your code above.")
    else:
        st.info("Run a bug fix to see results here.")

with tab3:
    st.subheader("📈 History")
    
    if 'history' in st.session_state and st.session_state.history:
        # Show as a table
        history_data = []
        for entry in st.session_state.history[-10:][::-1]:  # Show last 10, newest first
            history_data.append({
                "Time": time.strftime("%H:%M:%S", time.localtime(entry['timestamp'])),
                "Issue": entry['issue'][:50] + "..." if len(entry['issue']) > 50 else entry['issue'],
                "Score": f"{entry['score']:.2f}",
                "Status": "✅" if entry['success'] else "❌"
            })
        
        st.dataframe(history_data, use_container_width=True)
        
        # Clear history button
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("No history yet. Fix some bugs!")

# Footer
st.divider()
st.caption("🤖 SWE Agent Lite v1.0 | Built with ❤️ for MNC AI Engineering Roles")

# Run instructions for API - FIXED VERSION
if not st.session_state.get('api_started', False):
    st.sidebar.info(
        "**To start the API server:**\n"
        "```bash\n"
        "uvicorn app:app --reload\n"
        "```\n"
        "Then set API URL to `http://localhost:8000`"
    )