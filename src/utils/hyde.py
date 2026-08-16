import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

class HyDESearcher:
    """
    HyDE (Hypothetical Document Embeddings) search.
    Generates a hypothetical fixed version of the code,
    then uses it to find the most relevant files.
    """
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
            temperature=0.3,
        )
    
    def generate_hypothetical_code(self, issue: str) -> str:
        """Generate a hypothetical fixed version of the code."""
        prompt = f"""
        Given this bug report:
        {issue}
        
        Write a hypothetical Python function that fixes this bug.
        Include the function signature, proper error handling, and comments.
        This is just a hypothetical example, not the actual code.
        """
        
        messages = [
            SystemMessage(content="You are a senior engineer. Generate a hypothetical fixed code."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def search_with_hyde(self, issue: str, n_results: int = 3):
        """Use HyDE to search for relevant code."""
        print("🔮 Generating hypothetical code for search...")
        hypothetical = self.generate_hypothetical_code(issue)
        results = self.vector_store.search(hypothetical, n_results)
        return results