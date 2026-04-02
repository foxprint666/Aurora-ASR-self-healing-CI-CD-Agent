from typing import Dict, Tuple, Any, Optional
from environment.sandbox import Sandbox
from environment.observation_space import ObservationSpace
from environment.action_space import ActionSpace
from environment.reward_logic import RewardLogic
from environment.models import ASRObservation, ASRAction, ASRState, ASRReward
from openenv.core.env_server.interfaces import Environment

class ASREnvironment(Environment[ASRAction, ASRObservation, ASRState]):
    """
    Strict OpenEnv-v4 compliant environment for Aurora ASR.
    Inherits from openenv-core's Environment base class.
    """

    def __init__(
        self,
        repo_template: str = "sample_buggy_code",
        num_tests: int = 5,
        max_steps: int = 100,
        human_in_the_loop: bool = False,
        timeout: int = 30,
    ):
        super().__init__()
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

    @property
    def state(self) -> ASRState:
        """
        Get current environment state as a Pydantic model.
        Satisfies openenv-core's state property requirement.
        """
        return ASRState(
            episode_id=str(getattr(self.sandbox, 'id', 'default')),
            step_count=self.current_step,
            current_file=self.current_file,
            last_test_results=self.last_test_results or {},
            repo_template=self.repo_template
        )

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any
    ) -> ASRObservation:
        """
        Reset the environment for a new episode.
        Satisfies openenv-core's reset() signature.
        """
        if self.sandbox:
            self.sandbox.cleanup()
        
        self.sandbox = Sandbox(timeout=self.timeout)
        episode_dir = self.sandbox.create_episode_environment(self.repo_template)
        
        self.observation_builder = ObservationSpace(episode_dir)
        self.action_executor = ActionSpace(self.sandbox)
        
        self.current_step = 0
        self.current_file = None
        self.episode_reward = 0
        
        test_results = self.sandbox.run_pytest()
        self.last_test_results = test_results
        self.observation_builder.add_terminal_output(test_results.get("stdout", ""))
        
        obs_dict = self.observation_builder.get_observation(
            current_file=self.current_file,
            last_test_output=test_results
        )
        
        # Return Pydantic Observation
        return ASRObservation(
            **obs_dict,
            done=False,
            reward=0.0
        )

    def step(
        self,
        action: ASRAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any
    ) -> ASRObservation:
        """
        Execute one step in the environment.
        Satisfies openenv-core's step() signature.
        """
        self.current_step += 1
        
        # Execute action using the Action model's command/params
        result, info = self.action_executor.execute_action(action.command, action.params)
        
        if action.command == "read_file" and action.params.get("path"):
            self.current_file = action.params["path"]
            
        test_results = self.sandbox.run_pytest()
        self.last_test_results = test_results
        self.observation_builder.add_terminal_output(
            test_results.get("stdout", "") + "\n" + test_results.get("stderr", "")
        )
        
        # Compute Reward
        reward_value = self.reward_logic.compute_reward(action.command, info, test_results)
        self.episode_reward += reward_value
        
        # Create a Pydantic Reward Model
        asr_reward = ASRReward(
            value=reward_value,
            syntax_penalty=info.get("syntax_penalty", 0.0),
            test_bonus=info.get("test_bonus", 0.0),
            efficiency_bonus=-1.0 # Static step penalty for now
        )
        
        # Check termination
        failed_count = test_results.get("failed", 0)
        done = (failed_count == 0) or (self.current_step >= self.max_steps)
        
        obs_dict = self.observation_builder.get_observation(
            current_file=self.current_file,
            last_test_output=test_results
        )
        
        # Return Pydantic Observation with embedded Reward model
        return ASRObservation(
            **obs_dict,
            done=done,
            reward=reward_value,
            asr_reward=asr_reward
        )

    def close(self):
        """Clean up resources."""
        if self.sandbox:
            self.sandbox.cleanup()