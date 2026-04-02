from typing import Dict
import ast

class RewardLogic:
    """
    Computes rewards based on test results and actions.
    
    Rewards:
    +50 per test: Fail → Pass
    +200: All tests pass
    -100: SyntaxError
    -10: Illegal operation
    -1: Efficiency penalty per step
    +5: Human-in-the-loop feedback requested
    """

    def __init__(self, human_in_the_loop_enabled: bool = False, step_penalty: float = 1.0):
        """
        Initialize reward logic.
        
        Args:
            human_in_the_loop_enabled: Enable human feedback rewards
            step_penalty: Penalty per action taken to encourage speed
        """
        self.human_in_the_loop_enabled = human_in_the_loop_enabled
        self.step_penalty = step_penalty
        self.prev_test_results = None
        self.syntax_error_penalty_applied = False

    def compute_reward(
        self,
        action: str,
        action_result: Dict,
        test_results: Dict = None,
        is_human_approved: bool = False,
    ) -> float:
        """
        Compute reward for action.
        
        Args:
            action: Action taken
            action_result: Result from action execution
            test_results: Current test results (optional)
            is_human_approved: Whether action was approved by human
            
        Returns:
            Reward value (float)
        """
        reward = 0.0
        
        # Penalty for syntax errors
        if "error" in action_result and "SyntaxError" in action_result["error"]:
            if not self.syntax_error_penalty_applied:
                reward -= 100
                self.syntax_error_penalty_applied = True
        else:
            self.syntax_error_penalty_applied = False
        
        # Penalty for illegal operations
        if "error" in action_result:
            if "Access denied" in action_result["error"] or "PermissionError" in str(action_result["error"]):
                reward -= 10
        
        # Reward for test improvements
        if test_results and self.prev_test_results:
            reward += self._compute_test_reward(self.prev_test_results, test_results)
            self.prev_test_results = test_results
        elif test_results:
            self.prev_test_results = test_results
        
        # Human-in-the-loop reward
        if self.human_in_the_loop_enabled and is_human_approved:
            reward += 5
        
        return reward

    def _compute_test_reward(self, prev_results: Dict, curr_results: Dict) -> float:
        """
        Compute reward based on test state changes.
        
        Args:
            prev_results: Previous test results
            curr_results: Current test results
            
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Extract test counts
        prev_passed = prev_results.get("passed", 0)
        curr_passed = curr_results.get("passed", 0)
        prev_failed = prev_results.get("failed", 0)
        curr_failed = curr_results.get("failed", 0)
        
        # Reward for each test that goes from fail to pass
        tests_fixed = curr_passed - prev_passed
        if tests_fixed > 0:
            reward += tests_fixed * 50
        
        # Bonus for all tests passing
        if curr_failed == 0 and prev_failed > 0:
            reward += 200
        
        return reward

    def get_episodic_reward(self, test_results: Dict) -> float:
        """
        Compute episode reward (final score).
        
        Args:
            test_results: Final test results
            
        Returns:
            Episode reward
        """
        passed = test_results.get("passed", 0)
        failed = test_results.get("failed", 0)
        
        # Base reward: 100 points per passing test
        reward = passed * 100
        
        # Penalty for failures
        reward -= failed * 50
        
        # Bonus for perfect score
        if failed == 0:
            reward += 500
        
        return reward