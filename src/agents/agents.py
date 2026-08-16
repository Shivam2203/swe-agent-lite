import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from utils.tools import read_file, get_file_path, validate_python_syntax

load_dotenv()

# ✅ FIXED: Using currently active Groq models
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",  # Active replacement for decommissioned model
    temperature=0.3,
    max_tokens=1024,
)

# Alternative models if the above doesn't work:
# model="llama-3.1-8b-instant"  # Faster, slightly less capable
# model="mixtral-8x7b-32768"    # Good alternative
# model="gemma2-9b-it"          # Lightweight

def planner_node(state):
    """Reads the issue and locates the file to edit."""
    print("📋 PLANNER: Reading the issue...")
    file_path = get_file_path("buggy_script.py")
    file_content = read_file(file_path)
    
    return {
        "file_path": file_path,
        "file_content": file_content,
        "iteration": state.get("iteration", 0) + 1,
    }

def coder_node(state):
    """Generates a fixed version of the code."""
    print("💻 CODER: Writing the patch...")
    
    # Stop after 3 iterations to prevent infinite loop
    if state.get('iteration', 0) >= 3:
        print("⚠️ Max iterations reached. Stopping.")
        return {
            "proposed_patch": state.get('proposed_patch', '# No patch generated'),
            "history": [f"Iteration {state['iteration']}: Max iterations reached."]
        }
    
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
    """
    
    messages = [
        SystemMessage(content="You are an expert Python programmer who writes clean, bug-free code."),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        proposed_patch = response.content
        
        # Validate syntax
        is_valid, msg = validate_python_syntax(proposed_patch)
        if not is_valid:
            print(f"⚠️ Syntax validation failed: {msg}")
    
    except Exception as e:
        proposed_patch = state.get('file_content', '# Error: Could not generate patch')
        print(f"❌ CODER Error: {e}")
    
    print(f"✅ CODER: Generated patch (length: {len(proposed_patch)} chars)")
    
    return {
        "proposed_patch": proposed_patch,
        "history": [f"Iteration {state['iteration']}: Coder generated patch."]
    }

def critic_node(state):
    """Scores the proposed patch from 0 to 1."""
    print("🔍 CRITIC: Reviewing the patch...")
    
    # If we already have a high score, skip to save API calls
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
        SystemMessage(content="You are a strict code reviewer. You give honest, constructive scores."),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        output = response.content
        
        # Parse score and feedback
        score = 0.5
        feedback = "Unable to parse feedback."
        
        for line in output.split('\n'):
            if 'SCORE:' in line:
                try:
                    score = float(line.split(':')[1].strip())
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

def should_continue(state):
    """Decides whether to loop back to Coder or exit."""
    # Stop if score is good enough OR we've iterated 3 times
    if state.get('score', 0) >= 0.8 or state.get('iteration', 0) >= 3:
        print("🏁 FINAL: Stopping loop.")
        return "end"
    else:
        print("🔄 LOOP: Going back to Coder with feedback.")
        return "coder"