import gym
from gym import spaces
import os
from typing import Dict, Tuple
from environment.sandbox import Sandbox
from environment.observation_space import ObservationSpace
from environment.action_space import ActionSpace
from environment.reward_logic import RewardLogic

class ASREnvironment(gym.Env):
    """
    OpenEnv environment for Automated Software Repair.
    
    An agent must fix a buggy Python repository by:
    - Reading source files
    - Modifying code
    - Running tests
    - Learning from test results
    """

    metadata = {'render.modes': ['human']}

    def __init__(
        self,
        repo_template: str = "sample_buggy_code",
        num_tests: int = 5,
        max_steps: int = 100,
        human_in_the_loop: bool = False,
        timeout: int = 30,
    ):
        """
        Initialize ASR environment.
        
        Args:
            repo_template: Path to buggy repository template
            num_tests: Expected number of tests
            max_steps: Maximum steps per episode
            human_in_the_loop: Enable human feedback
            timeout: Subprocess timeout in seconds
        """
        super(ASREnvironment, self).__init__()
        
        self.repo_template = repo_template
        self.num_tests = num_tests
        self.max_steps = max_steps
        self.human_in_the_loop = human_in_the_loop
        self.timeout = timeout
        
        # Initialize components
        self.sandbox = None
        self.observation_builder = None
        self.action_executor = None
        self.reward_logic = RewardLogic(human_in_the_loop_enabled=human_in_the_loop)
        
        # State tracking
        self.current_step = 0
        self.current_file = None
        self.last_test_results = None
        self.episode_reward = 0
        
        # Gym spaces (simplified)
        self.action_space = spaces.Discrete(3)  # read, write, run_pytest
        self.observation_space = spaces.Dict({})  # Flexible observation space

    def reset(self) -> Dict:
        """
        Reset environment for new episode.
        
        Returns:
            Initial observation
        """
        # Cleanup previous episode
        if self.sandbox:
            self.sandbox.cleanup()
        
        # Create new sandbox
        self.sandbox = Sandbox(timeout=self.timeout)
        episode_dir = self.sandbox.create_episode_environment(self.repo_template)
        
        # Initialize components
        self.observation_builder = ObservationSpace(episode_dir)
        self.action_executor = ActionSpace(self.sandbox)
        self.reward_logic.prev_test_results = None
        
        # Reset state
        self.current_step = 0
        self.current_file = None
        self.episode_reward = 0
        
        # Run initial pytest to get baseline
        test_results = self.sandbox.run_pytest()
        self.last_test_results = test_results
        self.observation_builder.add_terminal_output(test_results["stdout"])
        
        return self.observation_builder.get_observation(
            current_file=self.current_file,
            last_test_output=test_results
        )

    def step(self, action: int, params: Dict = None) -> Tuple[Dict, float, bool, Dict]:
        """
        Execute one environment step.
        
        Args:
            action: Action ID (0=read_file, 1=write_file, 2=run_pytest)
            params: Action parameters
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        self.current_step += 1
        params = params or {}
        
        # Map action ID to action name
        action_names = ["read_file", "write_file", "run_pytest"]
        if action < 0 or action >= len(action_names):
            return self._get_observation(), -10, False, {"error": "Invalid action"}
        
        action_name = action_names[action]
        
        # Execute action
        result, info = self.action_executor.execute_action(action_name, params)
        
        # Update current file if reading
        if action_name == "read_file" and params.get("path"):
            self.current_file = params["path"]
        
        # Run pytest if not already done
        if action_name != "run_pytest":
            test_results = self.sandbox.run_pytest()
        else:
            test_results = result if result else {}
        
        self.last_test_results = test_results
        self.observation_builder.add_terminal_output(
            test_results.get("stdout", "") + "\n" + test_results.get("stderr", "")
        )
        
        # Compute reward
        reward = self.reward_logic.compute_reward(action_name, info, test_results)
        self.episode_reward += reward
        
        # Check if done
        failed_count = test_results.get("failed", 0)
        all_passed = failed_count == 0
        done = all_passed or self.current_step >= self.max_steps
        
        # Get observation
        obs = self._get_observation()
        
        info.update({
            "step": self.current_step,
            "total_reward": self.episode_reward,
            "tests_passed": test_results.get("passed", 0),
            "tests_failed": test_results.get("failed", 0),
        })
        
        return obs, reward, done, info

    def _get_observation(self) -> Dict:
        """Build current observation."""
        return self.observation_builder.get_observation(
            current_file=self.current_file,
            last_test_output=self.last_test_results
        )

    def render(self, mode='human'):
        """Render environment state."""
        print(f"\n--- Step {self.current_step} ---")
        print(f"Episode Reward: {self.episode_reward}")
        if self.last_test_results:
            print(f"Tests: {self.last_test_results.get('passed', 0)} passed, "
                  f"{self.last_test_results.get('failed', 0)} failed")

    def close(self):
        """Clean up resources."""
        if self.sandbox:
            self.sandbox.cleanup()