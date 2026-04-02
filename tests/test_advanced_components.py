"""
Tests for advanced components:
- Hybrid Actor-Critic Agent
- Dynamic Scenario Generator
- Hub Integration
"""

import unittest
import tempfile
import torch
from environment.scenario_generator import ScenarioGenerator
from agents.hybrid_actor_critic_agent import HybridActorCriticAgent, TransformerEncoder
from environment.gym_integration import ASREnvironmentHub, register_environments


class TestScenarioGenerator(unittest.TestCase):
    """Test scenario generation."""

    def test_generate_single_scenario(self):
        """Test single scenario generation."""
        gen = ScenarioGenerator(seed=42)
        scenario = gen.generate_scenario()
        
        self.assertIn("scenario_id", scenario)
        self.assertIn("bugs", scenario)
        self.assertIn("scenario_dir", scenario)

    def test_scenario_reproducibility(self):
        """Test scenarios are reproducible with same seed."""
        gen1 = ScenarioGenerator(seed=42)
        s1 = gen1.generate_scenario()
        
        gen2 = ScenarioGenerator(seed=42)
        s2 = gen2.generate_scenario()
        
        self.assertEqual(s1["bugs"], s2["bugs"])

    def test_batch_generation(self):
        """Test batch scenario generation."""
        gen = ScenarioGenerator(seed=42)
        scenarios = gen.generate_batch(10)
        
        self.assertEqual(len(scenarios), 10)


class TestTransformerEncoder(unittest.TestCase):
    """Test Transformer encoder."""

    def test_forward_pass(self):
        """Test encoder forward pass."""
        encoder = TransformerEncoder(input_dim=512, hidden_dim=256)
        
        batch = torch.randn(2, 10, 512)  # (batch, seq_len, dim)
        output = encoder(batch)
        
        self.assertEqual(output.shape, (2, 256))

    def test_output_dimension(self):
        """Test output dimension."""
        encoder = TransformerEncoder(input_dim=512, hidden_dim=128)
        self.assertEqual(encoder.output_dim, 128)


class TestHybridActorCriticAgent(unittest.TestCase):
    """Test Hybrid Actor-Critic Agent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = HybridActorCriticAgent(
            input_dim=512,
            hidden_dim=128,
            num_actions=3,
            device='cpu'
        )

    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        self.assertIsNotNone(self.agent.policy_net)
        self.assertIsNotNone(self.agent.value_net)

    def test_get_action(self):
        """Test agent action selection."""
        obs = {
            "file_tree": "src/main.py",
            "current_file": "def foo(): pass",
            "parse_tree": {},
            "test_results": {"passed": 2, "failed": 3},
            "last_output": "FAILED",
        }
        
        action, confidence = self.agent.get_action(obs)
        
        self.assertIn("action", action)
        self.assertIn("params", action)
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)

    def test_model_save_load(self):
        """Test saving and loading model."""
        with tempfile.NamedTemporaryFile(suffix=".pt") as f:
            self.agent.save(f.name)
            
            new_agent = HybridActorCriticAgent(device='cpu')
            new_agent.load(f.name)
            
            self.assertIsNotNone(new_agent.policy_net)


class TestHubIntegration(unittest.TestCase):
    """Test Hub-ready integration."""

    def test_environment_registration(self):
        """Test environment registration."""
        register_environments()
        # Should not raise exception

    def test_environment_creation(self):
        """Test environment creation."""
        register_environments()
        env = ASREnvironmentHub(num_scenarios=10, seed=42)
        
        self.assertIsNotNone(env.action_space)
        self.assertIsNotNone(env.observation_space)

    def test_environment_reset(self):
        """Test environment reset."""
        register_environments()
        env = ASREnvironmentHub(num_scenarios=5)
        
        obs = env.reset()
        self.assertIsNotNone(obs)

    def test_metadata(self):
        """Test environment metadata."""
        register_environments()
        env = ASREnvironmentHub()
        
        metadata = env.get_metadata()
        self.assertIn("name", metadata)
        self.assertIn("features", metadata)


if __name__ == '__main__':
    unittest.main()