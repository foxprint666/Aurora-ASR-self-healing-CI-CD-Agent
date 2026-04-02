from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from openenv.core.env_server.types import Action, Observation, State

class ASRReward(BaseModel):
    """
    Dedicated Pydantic model for ASR rewards.
    Splits the reward into component scores for transparency.
    """
    value: float = Field(description="The scalar reward value")
    syntax_penalty: float = Field(default=0.0, description="Penalty for invalid syntax")
    test_bonus: float = Field(default=0.0, description="Bonus for passing tests")
    efficiency_bonus: float = Field(default=0.0, description="Bonus/penalty based on steps taken")

class ASRObservation(Observation):
    """
    OpenEnv-compliant observation model for ASR.
    Includes ASR-specific fields like file tree and parse tree.
    """
    file_tree: str = Field(description="Visual representation of the workspace")
    current_file: str = Field(description="Path to the file currently being analyzed")
    test_results: Dict[str, Any] = Field(default_factory=dict, description="Pytest summary info")
    parse_tree: Dict[str, Any] = Field(default_factory=dict, description="AST nodes as JSON")
    last_output: str = Field(default="", description="Recent terminal logs")
    
    # Custom ASR-specific Reward Model
    asr_reward: Optional[ASRReward] = Field(default=None, description="Detailed Pydantic Reward breakdown")

class ASRAction(Action):
    """
    OpenEnv-compliant action model for ASR.
    Agents use this to command read/write/test operations.
    """
    command: str = Field(description="Action name (read_file, write_file, run_pytest)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the command")

class ASRState(State):
    """
    OpenEnv-compliant state model for ASR tracking.
    """
    current_file: Optional[str] = Field(default=None)
    last_test_results: Dict[str, Any] = Field(default_factory=dict)
    repo_template: str = Field(default="sample_buggy_code")
