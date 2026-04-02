"""
Hybrid Actor-Critic Agent for Automated Software Repair.

Architecture:
- Transformer-based encoder for state representation
- Dual-head network: Policy (Actor) & Value (Critic)
- PPO training algorithm
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from typing import Tuple, Dict, Any
import numpy as np
from agents.base_agent import BaseAgent


class TransformerEncoder(nn.Module):
    """
    Transformer-based state encoder.
    Processes file content, parse trees, and terminal output.
    """

    def __init__(self, input_dim: int = 512, hidden_dim: int = 256, num_heads: int = 4, num_layers: int = 2):
        """
        Initialize Transformer encoder.
        
        Args:
            input_dim: Input embedding dimension
            hidden_dim: Hidden dimension
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
        """
        super(TransformerEncoder, self).__init__()
        
        self.embedding = nn.Linear(input_dim, hidden_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 4,
            batch_first=True,
            dropout=0.1
        )
        
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )
        
        self.output_dim = hidden_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor (batch, seq_len, input_dim)
            
        Returns:
            Encoded representation (batch, seq_len, hidden_dim)
        """
        x = self.embedding(x)
        x = self.transformer_encoder(x)
        # Pool over sequence dimension
        x = x.mean(dim=1)
        return x


class PolicyNetwork(nn.Module):
    """
    Actor network: Maps observations to action probabilities.
    """

    def __init__(self, encoder: TransformerEncoder, hidden_dim: int = 256, num_actions: int = 3):
        """
        Initialize policy network.
        
        Args:
            encoder: Transformer encoder
            hidden_dim: Hidden dimension
            num_actions: Number of possible actions
        """
        super(PolicyNetwork, self).__init__()
        
        self.encoder = encoder
        
        self.mlp = nn.Sequential(
            nn.Linear(encoder.output_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        
        self.policy_head = nn.Linear(hidden_dim, num_actions)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass to get action probabilities.
        
        Args:
            state: State representation
            
        Returns:
            Action logits (batch, num_actions)
        """
        encoded = self.encoder(state)
        hidden = self.mlp(encoded)
        logits = self.policy_head(hidden)
        return logits

    def get_action_probs(self, state: torch.Tensor) -> torch.Tensor:
        """
        Get action probabilities.
        
        Args:
            state: State representation
            
        Returns:
            Action probabilities (batch, num_actions)
        """
        logits = self.forward(state)
        probs = self.softmax(logits)
        return probs


class ValueNetwork(nn.Module):
    """
    Critic network: Estimates state value.
    """

    def __init__(self, encoder: TransformerEncoder, hidden_dim: int = 256):
        """
        Initialize value network.
        
        Args:
            encoder: Transformer encoder
            hidden_dim: Hidden dimension
        """
        super(ValueNetwork, self).__init__()
        
        self.encoder = encoder
        
        self.mlp = nn.Sequential(
            nn.Linear(encoder.output_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        
        self.value_head = nn.Linear(hidden_dim, 1)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass to get state value.
        
        Args:
            state: State representation
            
        Returns:
            State value (batch, 1)
        """
        encoded = self.encoder(state)
        hidden = self.mlp(encoded)
        value = self.value_head(hidden)
        return value


class HybridActorCriticAgent(BaseAgent):
    """
    Hybrid Actor-Critic Agent for code repair.
    
    Combines:
    - Transformer encoder for state representation
    - Actor (policy) network for action selection
    - Critic (value) network for advantage estimation
    - PPO training algorithm
    """

    def __init__(
        self,
        input_dim: int = 512,
        hidden_dim: int = 256,
        num_actions: int = 3,
        learning_rate: float = 3e-4,
        use_tree_sitter: bool = True,
        device: str = 'cpu'
    ):
        """
        Initialize Hybrid Actor-Critic Agent.
        
        Args:
            input_dim: Input embedding dimension
            hidden_dim: Hidden dimension
            num_actions: Number of actions
            learning_rate: Learning rate for optimization
            use_tree_sitter: Use AST parsing
            device: Device to run on ('cpu' or 'cuda')
        """
        super().__init__(use_tree_sitter=use_tree_sitter)
        
        self.device = device
        self.num_actions = num_actions
        
        # Shared Transformer encoder
        self.encoder = TransformerEncoder(input_dim, hidden_dim)
        
        # Actor and Critic networks
        self.policy_net = PolicyNetwork(self.encoder, hidden_dim, num_actions).to(device)
        self.value_net = ValueNetwork(self.encoder, hidden_dim).to(device)
        
        # Optimizers
        self.policy_optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        self.value_optimizer = optim.Adam(self.value_net.parameters(), lr=learning_rate)
        
        # Experience buffer
        self.experience_buffer = {
            "states": [],
            "actions": [],
            "rewards": [],
            "values": [],
            "log_probs": [],
        }
        
        # Hyperparameters
        self.gamma = 0.99  # Discount factor
        self.gae_lambda = 0.95  # GAE parameter
        self.entropy_coef = 0.01  # Entropy regularization
        self.value_loss_coef = 0.5  # Value loss weight
        
        # Action mappings
        self.action_names = ["read_file", "write_file", "run_pytest"]

    def get_action(self, observation: Dict) -> Tuple[Dict, float]:
        """
        Choose action based on observation.
        
        Args:
            observation: Current environment observation
            
        Returns:
            Tuple of (action dict, confidence)
        """
        self.last_observation = observation
        
        # Encode observation
        state_tensor = self._encode_observation(observation)
        
        with torch.no_grad():
            # Get action probabilities from policy network
            action_probs = self.policy_net.get_action_probs(state_tensor)
            action_probs = action_probs.squeeze(0)  # Remove batch dimension
            
            # Get state value from critic network
            state_value = self.value_net(state_tensor).squeeze(0).item()
            
            # Sample action
            dist = torch.distributions.Categorical(action_probs)
            action_idx = dist.sample()
            log_prob = dist.log_prob(action_idx).item()
            
            confidence = action_probs[action_idx].item()
        
        # Store experience
        self.experience_buffer["states"].append(state_tensor.detach())
        self.experience_buffer["actions"].append(action_idx.item())
        self.experience_buffer["log_probs"].append(log_prob)
        self.experience_buffer["values"].append(state_value)
        
        action_name = self.action_names[action_idx]
        action_params = self._get_action_params(observation, action_name)
        
        return {
            "action": action_name,
            "params": action_params
        }, confidence

    def _encode_observation(self, observation: Dict) -> torch.Tensor:
        """
        Encode observation to state tensor.
        
        Args:
            observation: Raw observation dict
            
        Returns:
            State tensor (1, seq_len, input_dim)
        """
        features = []
        
        # Extract file tree features
        file_tree = observation.get("file_tree", "")
        file_tree_encoded = self._text_to_tensor(file_tree, max_len=100)
        features.append(file_tree_encoded)
        
        # Extract file content features
        current_file = observation.get("current_file", "")
        file_content_encoded = self._text_to_tensor(current_file, max_len=200)
        features.append(file_content_encoded)
        
        # Extract parse tree features (simplified)
        parse_tree = observation.get("parse_tree", {})
        parse_tree_encoded = self._tree_to_tensor(parse_tree, max_len=100)
        features.append(parse_tree_encoded)
        
        # Extract test results features
        test_results = observation.get("test_results", {})
        test_results_encoded = self._test_results_to_tensor(test_results)
        features.append(test_results_encoded)
        
        # Concatenate all features
        state = torch.cat(features, dim=1)
        
        return state.to(self.device)

    def _text_to_tensor(self, text: str, max_len: int = 100) -> torch.Tensor:
        """
        Convert text to embedding tensor.
        
        Args:
            text: Text content
            max_len: Maximum length
            
        Returns:
            Tensor of shape (1, max_len, 512)
        """
        # Simple character-level encoding
        text = text[:max_len * 10]  # Truncate
        
        # Character embeddings (simplified: ASCII values)
        char_codes = np.array([ord(c) % 128 for c in text], dtype=np.float32)
        
        # Pad or truncate
        if len(char_codes) < max_len:
            char_codes = np.pad(char_codes, (0, max_len - len(char_codes)))
        else:
            char_codes = char_codes[:max_len]
        
        # Expand to embedding dimension (512)
        tensor = torch.from_numpy(char_codes).unsqueeze(0).unsqueeze(0)
        tensor = tensor.expand(1, max_len, 512).float()
        
        return tensor

    def _tree_to_tensor(self, tree: Dict, max_len: int = 100) -> torch.Tensor:
        """
        Convert parse tree to tensor.
        
        Args:
            tree: Parse tree dict
            max_len: Maximum length
            
        Returns:
            Tensor of shape (1, max_len, 512)
        """
        # Flatten tree to sequence
        tree_str = str(tree)[:max_len * 10]
        
        return self._text_to_tensor(tree_str, max_len)

    def _test_results_to_tensor(self, results: Dict) -> torch.Tensor:
        """
        Convert test results to tensor.
        
        Args:
            results: Test results dict
            
        Returns:
            Tensor of shape (1, 10, 512)
        """
        # Extract numerical features
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        
        features = np.array([
            float(passed),
            float(failed),
            float(passed + failed) if (passed + failed) > 0 else 0,
            float(passed) / (passed + failed) if (passed + failed) > 0 else 0,
        ], dtype=np.float32)
        
        # Expand to (1, 10, 512)
        features = np.pad(features, (0, 10 - len(features)))
        tensor = torch.from_numpy(features).unsqueeze(0).unsqueeze(0)
        tensor = tensor.expand(1, 10, 512).float()
        
        return tensor

    def _get_action_params(self, observation: Dict, action_name: str) -> Dict:
        """
        Generate action parameters based on observation.
        
        Args:
            observation: Current observation
            action_name: Action name
            
        Returns:
            Action parameters
        """
        if action_name == "read_file":
            file_tree = observation.get("file_tree", "")
            lines = file_tree.split('\n')
            
            # Find first unread .py file
            for line in lines:
                if '.py' in line and 'src' in line:
                    return {"path": line.strip().split()[-1]}
            
            return {"path": "src/main.py"}
        
        elif action_name == "write_file":
            # Get suggestions from error analysis
            last_output = observation.get("last_output", "")
            
            if "NameError" in last_output:
                return {
                    "path": "src/main.py",
                    "content": "# Fixed variable reference\n"
                }
            elif "TypeError" in last_output:
                return {
                    "path": "src/main.py",
                    "content": "# Fixed type issue\n"
                }
            else:
                return {
                    "path": "src/main.py",
                    "content": "# General fix\n"
                }
        
        return {}

    def update(self, rewards: list):
        """
        Update networks based on collected experience (PPO).
        
        Args:
            rewards: List of rewards from episode
        """
        if len(self.experience_buffer["states"]) == 0:
            return
        
        # Convert to tensors
        states = torch.stack(self.experience_buffer["states"]).to(self.device)
        actions = torch.tensor(self.experience_buffer["actions"], device=self.device)
        old_log_probs = torch.tensor(self.experience_buffer["log_probs"], device=self.device)
        values = torch.tensor(self.experience_buffer["values"], device=self.device)
        rewards_tensor = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        
        # Compute advantages (GAE)
        advantages = self._compute_gae(rewards_tensor, values)
        
        # Update policy (Actor) - maximize advantage
        action_probs = self.policy_net.get_action_probs(states)
        action_dist = torch.distributions.Categorical(action_probs)
        new_log_probs = action_dist.log_prob(actions)
        
        ratio = torch.exp(new_log_probs - old_log_probs)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 0.8, 1.2) * advantages
        
        policy_loss = -torch.min(surr1, surr2).mean()
        entropy = action_dist.entropy().mean()
        
        total_policy_loss = policy_loss - self.entropy_coef * entropy
        
        self.policy_optimizer.zero_grad()
        total_policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 0.5)
        self.policy_optimizer.step()
        
        # Update value (Critic) - minimize value loss
        value_pred = self.value_net(states).squeeze(-1)
        value_target = rewards_tensor + self.gamma * values
        
        value_loss = F.mse_loss(value_pred, value_target)
        
        self.value_optimizer.zero_grad()
        value_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.value_net.parameters(), 0.5)
        self.value_optimizer.step()
        
        # Clear buffer
        self.experience_buffer = {
            "states": [],
            "actions": [],
            "rewards": [],
            "values": [],
            "log_probs": [],
        }

    def _compute_gae(self, rewards: torch.Tensor, values: torch.Tensor) -> torch.Tensor:
        """
        Compute Generalized Advantage Estimation (GAE).
        
        Args:
            rewards: Rewards tensor
            values: State values tensor
            
        Returns:
            Advantages tensor
        """
        advantages = []
        gae = 0
        
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]
            
            delta = rewards[t] + self.gamma * next_value - values[t]
            gae = delta + self.gamma * self.gae_lambda * gae
            advantages.insert(0, gae)
        
        return torch.tensor(advantages, dtype=torch.float32, device=self.device)

    def save(self, path: str):
        """Save model checkpoint."""
        torch.save({
            'policy_net': self.policy_net.state_dict(),
            'value_net': self.value_net.state_dict(),
        }, path)

    def load(self, path: str):
        """Load model checkpoint."""
        checkpoint = torch.load(path, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint['policy_net'])
        self.value_net.load_state_dict(checkpoint['value_net'])