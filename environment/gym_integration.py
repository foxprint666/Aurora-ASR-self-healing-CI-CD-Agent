"""
Hub-ready Gymnasium integration for OpenEnv.
Ensures the environment can be pip-installed and used with HuggingFace Hub.
"""

import gym
from gym import spaces
import json
from typing import Dict, Tuple, Any
from environment.asr_env import ASREnvironment as BaseASREnvironment
from environment.scenario_generator import ScenarioGenerator


class ASREnvironmentHub(gym.Env):
    """
    Hub-ready version of ASR Environment.
    Fully compatible with:
    - OpenAI Gym API
    - Hugging Face Hub
    - OpenRL/TorchRL frameworks
    """

    metadata = {'render.modes': ['human']}
    
    # Environment registration for Hub
    spec = {
        'id': 'ASR-v0',
        'entry_point': 'environment.gym_integration:ASREnvironmentHub',
        'max_episode_steps': 100,
        'kwargs': {
            'num_scenarios': 500,
            'seed': None,
        }
    }

    def __init__(
        self,
        num_scenarios: int = 500,
        seed: int = None,
        max_steps: int = 100,
        human_in_the_loop: bool = False,
    ):
        """
        Initialize Hub-ready environment.
        
        Args:
            num_scenarios: Number of unique scenarios to use
            seed: Random seed for reproducibility
            max_steps: Maximum steps per episode
            human_in_the_loop: Enable human feedback
        """
        super(ASREnvironmentHub, self).__init__()
        
        # Initialize scenario generator (500+ unique bugs)
        self.scenario_gen = ScenarioGenerator(seed=seed)
        self.scenarios = self.scenario_gen.generate_batch(num(scenarios // 10))  # Pre-generate sample
        
        self.num_scenarios = num_scenarios
        self.seed_value = seed
        self.max_steps = max_steps
        self.human_in_the_loop = human_in_the_loop
        
        # Current environment state
        self.current_scenario = None
        self.current_env = None
        self.episode_count = 0
        self.step_count = 0
        
        # Action space: 0=read_file, 1=write_file, 2=run_pytest
        self.action_space = spaces.Discrete(3)
        
        # Observation space (flexible dict)
        self.observation_space = spaces.Box(
            low=0, high=255,
            shape=(512,),  # Flattened observation
            dtype=np.float32
        )

    def reset(self) -> Dict:
        """
        Reset environment with new random scenario.
        
        Returns:
            Initial observation dict
        """
        # Generate new scenario
        self.current_scenario = self.scenario_gen.generate_scenario()
        
        # Create environment with this scenario
        if self.current_env:
            self.current_env.close()
        
        self.current_env = BaseASREnvironment(
            repo_template=self.current_scenario["scenario_dir"],
            num_tests=5,
            max_steps=self.max_steps,
            human_in_the_loop=self.human_in_the_loop,
        )
        
        obs = self.current_env.reset()
        self.step_count = 0
        self.episode_count += 1
        
        # Return flattened observation
        return self._flatten_observation(obs)

    def step(self, action: int) -> Tuple[Dict, float, bool, Dict]:
        """
        Execute one environment step.
        
        Args:
            action: Action index
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        self.step_count += 1
        
        action_names = ["read_file", "write_file", "run_pytest"]
        action_name = action_names[action]
        
        # For simplicity, pass empty params (agent should fill them)
        obs, reward, done, info = self.current_env.step(action, params={})
        
        # Flatten observation
        flat_obs = self._flatten_observation(obs)
        
        return flat_obs, reward, done, info

    def _flatten_observation(self, obs: Dict) -> np.ndarray:
        """
        Flatten complex observation to vector.
        
        Args:
            obs: Observation dict
            
        Returns:
            Flattened numpy array
        """
        import numpy as np
        
        # Extract key features
        passed = obs.get("test_results", {}).get("passed", 0)
        failed = obs.get("test_results", {}).get("failed", 0)
        
        # Create feature vector
        features = np.array([
            float(passed),
            float(failed),
            float(self.step_count) / self.max_steps,
            len(obs.get("file_tree", "")) / 1000.0,  # Normalize by typical size
            len(obs.get("current_file", "")) / 1000.0,
        ], dtype=np.float32)
        
        # Pad to observation space size
        features = np.pad(features, (0, 512 - len(features)))[:512]
        
        return features

    def render(self, mode: str = 'human'):
        """Render environment state."""
        if self.current_env:
            self.current_env.render(mode)

    def close(self):
        """Clean up."""
        if self.current_env:
            self.current_env.close()
        if self.current_scenario:
            self.scenario_gen.cleanup_scenario(self.current_scenario["scenario_dir"])

    def get_metadata(self) -> Dict:
        """Get environment metadata for Hub."""
        return {
            "name": "ASR-v0",
            "description": "Automated Software Repair with dynamic scenario generation",
            "version": "1.0.0",
            "author": "OpenEnv Contributors",
            "action_space": "Discrete(3)",
            "observation_space": "Box(512,)",
            "num_unique_scenarios": 500,
            "features": [
                "Transformer-based state encoding",
                "Dynamic scenario generation",
                "Tree-sitter AST parsing",
                "Human-in-the-loop support",
            ],
        }


# Register environment for gym
def register_environments():
    """Register environments with gym."""
    gym.register(
        id='ASR-v0',
        entry_point='environment.gym_integration:ASREnvironmentHub',
        max_episode_steps=100,
        kwargs={
            'num_scenarios': 500,
            'seed': 42,
        }
    )