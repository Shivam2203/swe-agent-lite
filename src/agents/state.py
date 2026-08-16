# from typing import TypedDict, List, Annotated
# import operator

# # This is the "Memory" of our agent. 
# # It carries information from one step to the next.
# class AgentState(TypedDict):
#     # The user's original request (e.g., "Fix division by zero bug")
#     issue: str
    
#     # The content of the file we are editing
#     file_content: str
    
#     # The file path we are editing
#     file_path: str
    
#     # The new code proposed by the Coder agent
#     proposed_patch: str
    
#     # The score given by the Critic (0 to 1)
#     score: float
    
#     # Feedback from Critic to Coder (e.g., "Missing try-except block")
#     feedback: str
    
#     # The number of loops we have done (max 3)
#     iteration: int
    
#     # History of all attempts (for debugging and resume talk)
#     # Annotated with operator.add allows us to append to this list
#     history: Annotated[List[str], operator.add]


from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    issue: str
    file_content: str
    file_path: str
    proposed_patch: str
    score: float
    feedback: str
    iteration: int
    history: Annotated[List[str], operator.add]