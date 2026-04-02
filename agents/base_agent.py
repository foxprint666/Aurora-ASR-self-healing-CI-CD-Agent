from abc import ABC, abstractmethod
from typing import Tuple, Dict

class BaseAgent(ABC):
    """
    Base class for repair agents.
    
    Agents receive observations and must choose actions to fix code.
    """

    def __init__(self, use_tree_sitter: bool = True):
        """
        Initialize agent.
        
        Args:
            use_tree_sitter: Use parsed AST or raw text
        """
        self.use_tree_sitter = use_tree_sitter
        self.last_observation = None

    @abstractmethod
    def get_action(self, observation: Dict) -> Tuple[str, float]:
        """
        Choose action based on observation.
        
        Args:
            observation: Current environment observation
            
        Returns:
            Tuple of (action, confidence)
        """
        pass

    def get_action_params(self, observation: Dict, action: str) -> Dict:
        """
        Get parameters for action.
        
        Args:
            observation: Current observation
            action: Action name
            
        Returns:
            Action parameters
        """
        return {}