"""
Evaluation script for trained agents.
Measures performance across diverse scenarios.
"""

import torch
import numpy as np
import argparse
from pathlib import Path

from environment.gym_integration import ASREnvironmentHub, register_environments
from agents.hybrid_actor_critic_agent import HybridActorCriticAgent


def evaluate_agent(
    checkpoint_path: str,
    num_scenarios: int = 50,
    device: str = 'cpu',
):
    """
    Evaluate trained agent.
    
    Args:
        checkpoint_path: Path to saved agent checkpoint
        num_scenarios: Number of test scenarios
        device: Device to use
        
    Returns:
        Dict with evaluation metrics
    """
    print(f"📊 Evaluating agent from: {checkpoint_path}")
    print(f"   Test scenarios: {num_scenarios}")
    print()
    
    # Register environments
    register_environments()
    
    # Create environment
    env = ASREnvironmentHub(num_scenarios=num_scenarios, seed=123)
    
    # Load agent
    agent = HybridActorCriticAgent(device=device)
    agent.load(checkpoint_path)
    agent.policy_net.eval()
    agent.value_net.eval()
    
    # Evaluate
    metrics = {
        "episode_rewards": [],
        "episode_lengths": [],
        "success_rate": 0,
        "avg_tests_fixed": [],
    }
    
    for scenario_id in range(num_scenarios):
        obs = env.reset()
        episode_reward = 0
        episode_length = 0
        tests_fixed = 0
        
        done = False
        with torch.no_grad():
            while not done:
                action_dict, confidence = agent.get_action({
                    "file_tree": "",
                    "current_file": "",
                    "parse_tree": {},
                    "test_results": {"passed": 0, "failed": 5},
                    "last_output": "",
                })
                
                action_idx = 0 if action_dict["action"] == "read_file" else (
                    1 if action_dict["action"] == "write_file" else 2
                )
                
                obs, reward, done, info = env.step(action_idx)
                
                episode_reward += reward
                episode_length += 1
                tests_fixed = info.get("tests_passed", 0)
        
        metrics["episode_rewards"].append(episode_reward)
        metrics["episode_lengths"].append(episode_length)
        metrics["avg_tests_fixed"].append(tests_fixed)
        
        if (scenario_id + 1) % 10 == 0:
            print(f"Evaluated {scenario_id + 1}/{num_scenarios} scenarios")
    
    # Compute statistics
    metrics["success_rate"] = sum(1 for r in metrics["episode_rewards"] if r > 200) / num_scenarios
    metrics["mean_reward"] = np.mean(metrics["episode_rewards"])
    metrics["mean_length"] = np.mean(metrics["episode_lengths"])
    metrics["mean_tests_fixed"] = np.mean(metrics["avg_tests_fixed"])
    
    # Print results
    print("\n" + "=" * 50)
    print("Evaluation Results")
    print("=" * 50)
    print(f"Success Rate: {metrics['success_rate']:.2%}")
    print(f"Mean Reward: {metrics['mean_reward']:.2f}")
    print(f"Mean Episode Length: {metrics['mean_length']:.1f}")
    print(f"Mean Tests Fixed: {metrics['mean_tests_fixed']:.2f}/5")
    print("=" * 50 + "\n")
    
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate trained agent")
    parser.add_argument("checkpoint", help="Path to agent checkpoint")
    parser.add_argument("--scenarios", type=int, default=50, help="Number of test scenarios")
    parser.add_argument("--device", default='cpu', help="Device")
    
    args = parser.parse_args()
    
    evaluate_agent(args.checkpoint, args.scenarios, args.device)