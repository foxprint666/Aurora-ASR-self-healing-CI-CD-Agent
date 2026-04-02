"""
Training script for Hybrid Actor-Critic Agent on ASR environment.
Hub-ready and fully decoupled from environment implementation.
"""

import torch
import numpy as np
from typing import Dict, List
import argparse
from pathlib import Path

from environment.gym_integration import ASREnvironmentHub, register_environments
from agents.hybrid_actor_critic_agent import HybridActorCriticAgent


class Trainer:
    """Trainer for Hybrid Actor-Critic Agent."""

    def __init__(
        self,
        env_id: str = "ASR-v0",
        num_episodes: int = 100,
        learning_rate: float = 3e-4,
        device: str = 'cpu',
        save_dir: str = './checkpoints',
    ):
        """
        Initialize trainer.
        
        Args:
            env_id: Environment ID
            num_episodes: Number of training episodes
            learning_rate: Learning rate for agent
            device: Device to train on
            save_dir: Directory to save checkpoints
        """
        self.env_id = env_id
        self.num_episodes = num_episodes
        self.learning_rate = learning_rate
        self.device = device
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Register environments
        register_environments()
        
        # Create environment
        self.env = ASREnvironmentHub(num_scenarios=500, seed=42)
        
        # Create agent
        self.agent = HybridActorCriticAgent(
            input_dim=512,
            hidden_dim=256,
            num_actions=3,
            learning_rate=learning_rate,
            device=device,
        )
        
        # Tracking
        self.episode_rewards = []
        self.episode_lengths = []
        self.best_reward = -np.inf

    def train(self):
        """Run training loop."""
        print(f"🚀 Starting training on {self.device}")
        print(f"   Episodes: {self.num_episodes}")
        print(f"   Learning Rate: {self.learning_rate}")
        print()
        
        for episode in range(self.num_episodes):
            obs = self.env.reset()
            episode_reward = 0
            episode_length = 0
            episode_rewards = []
            
            done = False
            while not done:
                # Agent chooses action
                action_dict, confidence = self.agent.get_action({
                    "file_tree": "src/main.py\ntests/test_main.py",
                    "current_file": obs[:50].tolist(),
                    "parse_tree": {},
                    "test_results": {"passed": int(obs[0]), "failed": int(obs[1])},
                    "last_output": "",
                })
                
                # Execute action
                action_idx = 0 if action_dict["action"] == "read_file" else (
                    1 if action_dict["action"] == "write_file" else 2
                )
                
                obs, reward, done, info = self.env.step(action_idx)
                
                episode_reward += reward
                episode_length += 1
                episode_rewards.append(reward)
            
            # Update agent with episode experience
            self.agent.update(episode_rewards)
            
            # Track statistics
            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)
            
            # Logging
            if (episode + 1) % 10 == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                avg_length = np.mean(self.episode_lengths[-10:])
                
                print(f"Episode {episode + 1}/{self.num_episodes}")
                print(f"  Reward: {episode_reward:.2f} (avg: {avg_reward:.2f})")
                print(f"  Length: {episode_length} (avg: {avg_length:.1f})")
                print(f"  Tests Passed: {info.get('tests_passed', 0)}")
                print()
                
                # Save checkpoint if best so far
                if episode_reward > self.best_reward:
                    self.best_reward = episode_reward
                    self.save_checkpoint(episode, episode_reward)
        
        print("✅ Training complete!")
        self._print_statistics()

    def save_checkpoint(self, episode: int, reward: float):
        """Save agent checkpoint."""
        checkpoint_path = self.save_dir / f"agent_ep{episode}_reward{reward:.0f}.pt"
        self.agent.save(str(checkpoint_path))
        print(f"💾 Saved checkpoint: {checkpoint_path}")

    def _print_statistics(self):
        """Print training statistics."""
        print("\n" + "=" * 50)
        print("Training Statistics")
        print("=" * 50)
        print(f"Total Episodes: {len(self.episode_rewards)}")
        print(f"Best Episode Reward: {max(self.episode_rewards):.2f}")
        print(f"Average Episode Reward: {np.mean(self.episode_rewards):.2f}")
        print(f"Average Episode Length: {np.mean(self.episode_lengths):.1f}")
        print("=" * 50 + "\n")


def main():
    """Main training entry point."""
    parser = argparse.ArgumentParser(description="Train Hybrid Actor-Critic Agent")
    parser.add_argument("--episodes", type=int, default=100, help="Number of episodes")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--device", default='cpu', help="Device (cpu or cuda)")
    parser.add_argument("--save-dir", default='./checkpoints', help="Save directory")
    
    args = parser.parse_args()
    
    trainer = Trainer(
        num_episodes=args.episodes,
        learning_rate=args.lr,
        device=args.device,
        save_dir=args.save_dir,
    )
    
    trainer.train()


if __name__ == "__main__":
    main()