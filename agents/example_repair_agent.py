from agents.base_agent import BaseAgent
from typing import Tuple, Dict
import random

class RepairAgent(BaseAgent):
    """
    Example repair agent using simple heuristics.
    
    Strategy:
    1. Read all source files
    2. Parse with Tree-sitter
    3. Run tests to find failing tests
    4. Make targeted fixes
    5. Re-run tests
    """

    def __init__(self, use_tree_sitter: bool = True, human_in_the_loop_threshold: float = 0.9):
        """
        Initialize repair agent.
        
        Args:
            use_tree_sitter: Use AST parsing
            human_in_the_loop_threshold: Confidence threshold for asking human
        """
        super().__init__(use_tree_sitter=use_tree_sitter)
        self.human_in_the_loop_threshold = human_in_the_loop_threshold
        self.files_examined = set()
        self.current_fix_attempt = 0

    def get_action(self, observation: Dict) -> Tuple[str, float]:
        """
        Choose action based on observation.
        
        Strategy:
        1. First, read and analyze all source files
        2. Then try fixes based on error messages
        3. Ask human if confidence < threshold
        
        Args:
            observation: Current observation
            
        Returns:
            Tuple of (action dict, confidence)
        """
        self.last_observation = observation
        
        # Parse observation
        file_tree = observation.get("file_tree", "")
        current_file = observation.get("current_file", "")
        parse_tree = observation.get("parse_tree", {})
        test_results = observation.get("test_results", {})
        last_output = observation.get("last_output", "")
        
        # Extract failing tests
        failed_tests = []
        if "details" in test_results:
            failed_tests = [t for t in test_results["details"] if t.get("status") == "FAIL"]
        
        # Decision logic
        if not self.files_examined:
            # Phase 1: Explore source files
            return self._explore_files(file_tree)
        elif failed_tests:
            # Phase 2: Analyze and fix errors
            return self._fix_error(failed_tests, last_output, parse_tree)
        else:
            # Phase 3: Tests passing, try more improvements or finish
            return {"action": "run_pytest"}, 0.95

    def _explore_files(self, file_tree: str) -> Tuple[Dict, float]:
        """
        Explore source files to understand code structure.
        
        Args:
            file_tree: File tree representation
            
        Returns:
            Action and confidence
        """
        # Extract src/ files
        lines = file_tree.split('\n')
        src_files = [l.strip() for l in lines if l.strip().endswith('.py') and 'src' in l]
        
        # Pick first unexplored file
        for f in src_files:
            file_path = f.replace('src/', 'src/').strip()
            if file_path not in self.files_examined:
                self.files_examined.add(file_path)
                return {"action": "read_file", "path": file_path}, 0.9
        
        # All files explored
        return {"action": "run_pytest"}, 0.95

    def _fix_error(self, failed_tests: list, last_output: str, parse_tree: Dict) -> Tuple[Dict, float]:
        """
        Attempt to fix detected errors.
        
        Args:
            failed_tests: List of failing tests
            last_output: Last terminal output
            parse_tree: Parsed code tree
            
        Returns:
            Action and confidence
        """
        error_msg = last_output[-500:] if last_output else ""  # Last 500 chars
        
        # Detect common errors
        if "NameError" in error_msg:
            confidence = 0.7
            # Ask human for uncertain fixes
            if confidence < self.human_in_the_loop_threshold:
                return {"action": "request_human_input", "error": "NameError"}, confidence
            return {"action": "fix_undefined_variable"}, confidence
        
        elif "TypeError" in error_msg:
            return {"action": "fix_type_error"}, 0.6
        
        elif "IndexError" in error_msg:
            return {"action": "fix_index_error"}, 0.6
        
        else:
            # Unknown error, ask human
            return {"action": "request_human_input", "error": error_msg[-100:]}, 0.3

    def get_action_params(self, observation: Dict, action: str) -> Dict:
        """
        Get parameters for action.
        
        Args:
            observation: Current observation
            action: Action name
            
        Returns:
            Action parameters dict
        """
        if action == "read_file":
            return {"path": "src/main.py"}
        elif action == "write_file":
            return {
                "path": "src/main.py",
                "content": "# Fixed code here"
            }
        return {}