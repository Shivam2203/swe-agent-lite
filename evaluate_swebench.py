"""
SWE-bench Evaluation Script
Benchmarks your agent against real-world bugs from open-source projects
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, List, Optional
from dotenv import load_dotenv
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.state import AgentState
from agents.graph import build_graph
from utils.tools import write_file, read_file

load_dotenv()

class SWEbenchEvaluator:
    def __init__(self):
        """Initialize the SWE-bench evaluator."""
        self.agent = build_graph()
        self.results = []
    
    def get_sample_bugs(self) -> List[Dict]:
        """
        Returns a list of sample bugs for testing.
        These are simplified versions of real SWE-bench bugs.
        """
        return [
            {
                "instance_id": "pandas__bug_001",
                "repo": "pandas",
                "issue": "DataFrame.groupby() with as_index=False raises KeyError when grouping by a column that doesn't exist",
                "file_path": "pandas/core/groupby.py",
                "buggy_code": """
def groupby(self, by, axis=0, level=None, as_index=True, sort=True, group_keys=True, squeeze=False, observed=False):
    # BUG: Doesn't handle non-existent columns properly
    if isinstance(by, str):
        if by not in self.columns:
            raise KeyError(f"Column '{by}' not found")
    return GroupBy(self, by, axis=axis, level=level, as_index=as_index, sort=sort, 
                   group_keys=group_keys, squeeze=squeeze, observed=observed)
""",
                "expected_fix": "Should return empty GroupBy or handle gracefully"
            },
            {
                "instance_id": "scikit-learn__bug_002",
                "repo": "scikit-learn",
                "issue": "StandardScaler with with_mean=False and with_std=False raises error on sparse matrices",
                "file_path": "sklearn/preprocessing/data.py",
                "buggy_code": """
def transform(self, X, copy=None):
    # BUG: Doesn't handle sparse matrices with no scaling
    if self.with_mean and self.with_std:
        X = super().transform(X, copy=copy)
    elif self.with_mean:
        X = X - self.mean_
    elif self.with_std:
        X = X / self.scale_
    return X
""",
                "expected_fix": "Should handle both with_mean=False and with_std=False case"
            },
            {
                "instance_id": "django__bug_003",
                "repo": "django",
                "issue": "ModelAdmin.list_display with callable causes duplicate SQL queries in admin interface",
                "file_path": "django/contrib/admin/options.py",
                "buggy_code": """
def get_list_display(self, request):
    # BUG: Callable functions in list_display cause N+1 queries
    if hasattr(self, 'list_display') and callable(self.list_display):
        return self.list_display(request)
    return self.list_display
""",
                "expected_fix": "Should cache callable results or use prefetch_related"
            }
        ]
    
    def run_agent_on_bug(self, bug: Dict) -> Dict:
        """Run the agent on a single bug."""
        print(f"\n{'='*60}")
        print(f"🐛 Testing: {bug['instance_id']}")
        print(f"📝 Issue: {bug['issue'][:100]}...")
        print(f"{'='*60}")
        
        # Create temporary file with buggy code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(bug['buggy_code'])
            temp_path = f.name
        
        # Read the buggy code
        file_content = read_file(temp_path)
        
        # Initial state
        initial_state = {
            "issue": bug['issue'],
            "file_content": file_content,
            "file_path": temp_path,
            "proposed_patch": "",
            "score": 0.0,
            "feedback": "",
            "iteration": 0,
            "history": []
        }
        
        try:
            # Run the agent
            final_state = self.agent.invoke(initial_state)
            
            # Clean up
            os.unlink(temp_path)
            
            return {
                "instance_id": bug['instance_id'],
                "success": final_state['score'] >= 0.8,
                "score": final_state['score'],
                "iterations": final_state['iteration'],
                "feedback": final_state['feedback'],
                "proposed_patch": final_state.get('proposed_patch', ''),
                "expected_fix": bug['expected_fix']
            }
        except Exception as e:
            return {
                "instance_id": bug['instance_id'],
                "success": False,
                "score": 0.0,
                "iterations": 0,
                "feedback": f"Error: {e}",
                "proposed_patch": "",
                "expected_fix": bug['expected_fix']
            }
    
    def run_evaluation(self) -> Dict:
        """Run the full evaluation on all sample bugs."""
        print("🚀 Starting SWE-bench Evaluation...\n")
        
        bugs = self.get_sample_bugs()
        results = []
        
        for bug in bugs:
            result = self.run_agent_on_bug(bug)
            results.append(result)
            
            # Print result
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            print(f"\n{status} | Score: {result['score']:.2f} | Iterations: {result['iterations']}")
            if not result['success']:
                print(f"   Feedback: {result['feedback'][:100]}...")
        
        # Calculate metrics
        total = len(results)
        passed = sum(1 for r in results if r['success'])
        
        summary = {
            "total_bugs": total,
            "passed": passed,
            "passed_pct": (passed / total) * 100 if total > 0 else 0,
            "average_score": sum(r['score'] for r in results) / total if total > 0 else 0,
            "average_iterations": sum(r['iterations'] for r in results) / total if total > 0 else 0,
            "results": results
        }
        
        return summary
    
    def save_results(self, summary: Dict, output_file: str = "evaluation_results.json"):
        """Save evaluation results to a JSON file."""
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n📊 Results saved to: {output_file}")

def main():
    """Main evaluation function."""
    evaluator = SWEbenchEvaluator()
    summary = evaluator.run_evaluation()
    
    print("\n" + "="*60)
    print("📊 EVALUATION SUMMARY")
    print("="*60)
    print(f"Total Bugs: {summary['total_bugs']}")
    print(f"Passed: {summary['passed']}")
    print(f"Pass Rate: {summary['passed_pct']:.1f}%")
    print(f"Average Score: {summary['average_score']:.2f}")
    print(f"Average Iterations: {summary['average_iterations']:.1f}")
    print("="*60)
    
    # Save results
    evaluator.save_results(summary)
    
    # Detailed results
    print("\n📋 Detailed Results:")
    for result in summary['results']:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['instance_id']}: {result['score']:.2f}")

if __name__ == "__main__":
    main()