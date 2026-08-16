import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from utils.tools import read_file, get_file_path, validate_python_syntax
from utils.vector_store import CodeVectorStore
from utils.hyde import HyDESearcher

# Load environment variables
load_dotenv()

# ============================================================
# 1. INITIALIZE LLM (Groq)
# ============================================================
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",  # Active model as of Aug 2026
    temperature=0.3,
    max_tokens=1024,
)

# ============================================================
# 2. INITIALIZE VECTOR STORE & HYDE
# ============================================================
# Create vector store instance
vector_store = CodeVectorStore()

# Get the repo path (go up 2 levels from this file's location)
repo_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dummy_repo = os.path.join(repo_path, "dummy_repo")

# Index the dummy repository
vector_store.index_codebase(dummy_repo)

# Initialize HyDE searcher with the vector store
hyde_searcher = HyDESearcher(vector_store)


# ============================================================
# 3. AGENT 1: PLANNER (with HyDE search)
# ============================================================
def planner_node(state):
    """
    Reads the issue and uses HyDE to find the most relevant file.
    Falls back to default file if no results found.
    """
    print("📋 PLANNER: Analyzing issue with HyDE...")
    
    # Use HyDE to find the most relevant file
    results = hyde_searcher.search_with_hyde(state['issue'], n_results=1)
    
    if results:
        code, file_path = results[0]
        file_content = code
        print(f"📄 Found relevant file: {os.path.basename(file_path)}")
    else:
        # Fallback to default file
        file_path = get_file_path("buggy_script.py")
        file_content = read_file(file_path)
        print("📄 Using default file: buggy_script.py")
    
    return {
        "file_path": file_path,
        "file_content": file_content,
        "iteration": state.get("iteration", 0) + 1,
    }


# ============================================================
# 4. AGENT 2: CODER (generates the fix)
# ============================================================
def coder_node(state):
    """
    Generates a fixed version of the code.
    Uses feedback from Critic to improve iteratively.
    """
    print("💻 CODER: Writing the patch...")
    
    # Stop after 3 iterations to prevent infinite loop
    if state.get('iteration', 0) >= 3:
        print("⚠️ Max iterations reached. Stopping.")
        return {
            "proposed_patch": state.get('proposed_patch', '# No patch generated'),
            "history": [f"Iteration {state['iteration']}: Max iterations reached."]
        }
    
    # Build the prompt with feedback if available
    prompt = f"""
    You are a Senior Software Engineer. Fix the bug in the code below.
    
    ISSUE: {state['issue']}
    
    CURRENT CODE:
    {state['file_content']}
    
    FEEDBACK FROM LAST REVIEW (if any): {state.get('feedback', 'No feedback yet. Write the best fix.')}
    
    INSTRUCTIONS:
    1. Only output the ENTIRE corrected code. No explanations.
    2. Keep the same function name and structure.
    3. Handle edge cases (like division by zero, empty inputs).
    4. Use try-except blocks where appropriate.
    5. Add proper error messages.
    """
    
    messages = [
        SystemMessage(content="You are an expert Python programmer who writes clean, bug-free, production-ready code."),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        proposed_patch = response.content
        
        # Validate Python syntax
        is_valid, msg = validate_python_syntax(proposed_patch)
        if not is_valid:
            print(f"⚠️ Syntax validation failed: {msg}")
        else:
            print("✅ Syntax validation passed")
    
    except Exception as e:
        proposed_patch = state.get('file_content', '# Error: Could not generate patch')
        print(f"❌ CODER Error: {e}")
    
    print(f"✅ CODER: Generated patch (length: {len(proposed_patch)} chars)")
    
    return {
        "proposed_patch": proposed_patch,
        "history": [f"Iteration {state['iteration']}: Coder generated patch."]
    }


# ============================================================
# 5. AGENT 3: CRITIC (scores the code)
# ============================================================
def critic_node(state):
    """
    Scores the proposed patch from 0.0 to 1.0.
    Criteria:
    - Bug fixed? (0-0.5)
    - Clean code? (0-0.3)
    - Error handling? (0-0.2)
    """
    print("🔍 CRITIC: Reviewing the patch...")
    
    # Skip if already high score
    if state.get('score', 0) >= 0.8:
        print("✅ Score already high. Skipping critic.")
        return state
    
    prompt = f"""
    You are a Code Reviewer. Score the following patch from 0.0 to 1.0.
    
    ORIGINAL ISSUE: {state['issue']}
    
    PROPOSED PATCH:
    {state['proposed_patch']}
    
    SCORING CRITERIA:
    - Does it fix the issue? (0 to 0.5 points)
    - Is the code clean and handling edge cases? (0 to 0.3 points)
    - Does it have proper error handling? (0 to 0.2 points)
    
    OUTPUT FORMAT (EXACTLY):
    SCORE: 0.85
    FEEDBACK: The code handles division by zero but could add logging.
    """
    
    messages = [
        SystemMessage(content="You are a strict code reviewer. You give honest, constructive scores with actionable feedback."),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        output = response.content
        
        # Parse score and feedback
        score = 0.5  # Default
        feedback = "Unable to parse feedback."
        
        for line in output.split('\n'):
            if 'SCORE:' in line:
                try:
                    score = float(line.split(':')[1].strip())
                    # Clamp score between 0 and 1
                    score = max(0.0, min(1.0, score))
                except:
                    pass
            if 'FEEDBACK:' in line:
                feedback = line.split(':')[1].strip()
        
    except Exception as e:
        score = 0.5
        feedback = f"Critic error: {e}"
        print(f"❌ CRITIC Error: {e}")
    
    print(f"📊 CRITIC: Score = {score}, Feedback: {feedback[:50]}...")
    
    return {
        "score": score,
        "feedback": feedback,
        "history": [f"Iteration {state['iteration']}: Critic gave score {score}"]
    }


# ============================================================
# 6. CONDITIONAL EDGE (loop or stop)
# ============================================================
def should_continue(state):
    """
    Decides whether to loop back to Coder or exit.
    Stops if:
    - Score >= 0.8 (good enough)
    - Iteration >= 3 (max attempts)
    """
    if state.get('score', 0) >= 0.8 or state.get('iteration', 0) >= 3:
        print("🏁 FINAL: Stopping loop.")
        return "end"
    else:
        print("🔄 LOOP: Going back to Coder with feedback.")
        return "coder"