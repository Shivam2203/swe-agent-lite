import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.state import AgentState
from src.agents.agents import planner_node, coder_node, critic_node, should_continue
from src.utils.tools import validate_python_syntax

class TestAgents:
    def test_planner_node(self):
        state = {
            "issue": "Fix division by zero",
            "file_content": "",
            "file_path": "",
            "proposed_patch": "",
            "score": 0.0,
            "feedback": "",
            "iteration": 0,
            "history": []
        }
        result = planner_node(state)
        assert result['iteration'] == 1
        assert 'file_content' in result
        assert 'file_path' in result
    
    def test_coder_node(self):
        state = {
            "issue": "Fix division by zero",
            "file_content": "def divide(a, b): return a / b",
            "file_path": "dummy_repo/buggy_script.py",
            "proposed_patch": "",
            "score": 0.0,
            "feedback": "",
            "iteration": 0,
            "history": []
        }
        result = coder_node(state)
        assert result['proposed_patch'] != ""
        assert len(result['history']) == 1
    
    def test_should_continue(self):
        # Test stop condition (score >= 0.8)
        state = {
            "score": 0.85,
            "iteration": 1,
            "history": []
        }
        result = should_continue(state)
        assert result == "end"
        
        # Test stop condition (iteration >= 3)
        state = {
            "score": 0.5,
            "iteration": 3,
            "history": []
        }
        result = should_continue(state)
        assert result == "end"
        
        # Test continue condition
        state = {
            "score": 0.5,
            "iteration": 1,
            "history": []
        }
        result = should_continue(state)
        assert result == "coder"
    
    def test_validate_python_syntax(self):
        # Test valid code
        is_valid, msg = validate_python_syntax("x = 1 + 2")
        assert is_valid == True
        
        # Test invalid code
        is_valid, msg = validate_python_syntax("x = 1 +")
        assert is_valid == False