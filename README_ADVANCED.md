# OpenEnv Automated Software Repair (ASR) - Advanced Features

This document describes the advanced components of the ASR environment:
- **Hybrid Actor-Critic Agent** with Transformer encoders
- **Dynamic Scenario Generator** for 500+ unique bug patterns
- **Hub-Ready Integration** for Hugging Face Hub

---

## ���� Hybrid Actor-Critic Agent

### Architecture

```
    State Observation
           ↓
    [Transformer Encoder]
      (Shared backbone)
           ↓
      ┌────┴────┐
      ↓         ↓
   [Policy]  [Value]
   (Actor)   (Critic)
      ↓         ↓
  Actions   State Value
```

### Components

#### **Transformer Encoder** (Shared)
- **Input**: Raw state features (file content, parse trees, test results)
- **Architecture**: 2-layer transformer with 4 attention heads
- **Output**: 256-dim state representation

#### **Policy Network (Actor)**
- **Input**: Encoded state (256-dim)
- **Hidden**: 256-dim MLP with ReLU
- **Output**: Action logits (3 possible actions)
- **Purpose**: Learn optimal action distribution

#### **Value Network (Critic)**
- **Input**: Encoded state (256-dim)
- **Hidden**: 256-dim MLP with ReLU
- **Output**: State value estimate (scalar)
- **Purpose**: Estimate expected future rewards

### Training Algorithm: PPO (Proximal Policy Optimization)

```python
For each episode:
  1. Collect experience using current policy
  2. Compute advantages using GAE (Generalized Advantage Estimation)
  3. Update actor (policy) to maximize advantage
  4. Update critic (value) to minimize prediction error
  5. Regularize with entropy bonus
```

### Key Hyperparameters

```python
gamma = 0.99              # Discount factor
gae_lambda = 0.95         # GAE parameter
entropy_coef = 0.01       # Entropy regularization weight
learning_rate = 3e-4      # Adam optimizer learning rate
```

### Usage

```python
from agents.hybrid_actor_critic_agent import HybridActorCriticAgent
from environment.gym_integration import ASREnvironmentHub

# Initialize
agent = HybridActorCriticAgent(
    input_dim=512,
    hidden_dim=256,
    num_actions=3,
    learning_rate=3e-4,
    device='cuda'  # or 'cpu'
)

env = ASREnvironmentHub()

# Training loop
for episode in range(100):
    obs = env.reset()
    done = False
    
    while not done:
        action, confidence = agent.get_action(obs)
        obs, reward, done, info = env.step(action)
    
    # Update agent after episode
    agent.update(episode_rewards)

# Save checkpoint
agent.save('best_agent.pt')

# Load checkpoint
agent.load('best_agent.pt')
```

---

## 🎯 Dynamic Scenario Generator

Generates **500+ unique bug scenarios** to prevent overfitting and ensure the agent learns universal debugging principles.

### Problem Solved

**Without diversity**: Agent memorizes specific bugs
```
Training: fix_undefined_variable_x()
Testing: fix_undefined_variable_y()
Result: ❌ Fails on new variable names
```

**With ScenarioGenerator**: Agent learns principles
```
Training: 500+ unique scenarios with varied bugs
Testing: New scenarios with unseen bug patterns
Result: ✅ Generalizes to novel bugs
```

### Supported Bug Patterns

```python
BugTypes = [
    "undefined_variable",        # Reference to undefined var
    "type_mismatch",            # Mixing incompatible types
    "missing_return",           # Function missing return
    "off_by_one",               # List index errors
    "null_reference",           # Accessing None
    "wrong_logic",              # Incorrect conditionals
    "infinite_loop",            # Unintended loops
    "import_error",             # Missing imports
    "indentation_error",        # Python syntax
    "scope_issue",              # Variable scope problems
]
```

### Scenario Structure

Each generated scenario contains:

```
scenario_<id>/
├── src/
│   └── main.py               # Buggy code (1-3 bugs)
├── tests/
│   └── test_main.py          # 5 unit tests
└── pytest.ini

Metadata:
{
    "scenario_id": 42,
    "bugs": ["undefined_variable", "type_mismatch"],
    "bug_descriptions": [...]
}
```

### Usage

```python
from environment.scenario_generator import ScenarioGenerator

# Create generator with deterministic seed
gen = ScenarioGenerator(seed=42)

# Generate single scenario
scenario = gen.generate_scenario()
print(scenario["scenario_dir"])  # e.g., /tmp/scenario_1_xyz

# Generate batch
scenarios = gen.generate_batch(num_scenarios=100)

# Get statistics
stats = gen.get_statistics()
print(stats)
# Output:
# {
#     "total_scenarios_generated": 100,
#     "num_bug_templates": 10,
#     "seed": 42,
#     "bug_types": ["undefined_variable", "type_mismatch", ...]
# }

# Cleanup
gen.cleanup_scenario(scenario["scenario_dir"])
```

### Customization

Add custom bug patterns:

```python
from environment.scenario_generator import ScenarioGenerator, BugTemplate

def my_bug_generator(idx):
    return """def my_func(x):
    # Your custom bug here
    return x + undefined_var
"""

custom_template = BugTemplate(
    name="custom_bug",
    description="My custom bug pattern",
    generator_func=my_bug_generator
)

gen = ScenarioGenerator()
gen.bug_templates.append(custom_template)
```

### Statistics

**Diversity across 500 scenarios:**
- Scenarios with 1 bug: ~50%
- Scenarios with 2 bugs: ~35%
- Scenarios with 3 bugs: ~15%
- Each scenario is **unique** (no duplicates)

---

## 🌐 Hub-Ready Integration (Gymnasium)

### What Makes It "Hub-Ready"?

✅ **Standardized API**: Follows OpenAI Gym interface
✅ **One-line Install**: `pip install openenv-asr`
✅ **Decoupled Design**: Environment, Agent, Generator are independent
✅ **Hugging Face Compatible**: Can be registered on HF Hub
✅ **Reproducible**: Deterministic seeding across all components

### Registration

```python
import gym
from environment.gym_integration import register_environments

# Register all environments
register_environments()

# Create environment
env = gym.make('ASR-v0', num_scenarios=500, seed=42)

obs = env.reset()
for _ in range(100):
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    if done:
        break

env.close()
```

### Metadata for Hub

```python
{
    "name": "ASR-v0",
    "description": "Automated Software Repair with dynamic scenario generation",
    "version": "1.0.0",
    "action_space": "Discrete(3)",
    "observation_space": "Box(512,)",
    "num_unique_scenarios": 500,
    "features": [
        "Transformer-based encoding",
        "Dynamic scenario generation",
        "Tree-sitter AST parsing",
        "Human-in-the-loop support",
    ]
}
```

### API Compliance

```python
# Standard Gym API
env = gym.make('ASR-v0')

# reset() returns initial observation
obs = env.reset()

# step() returns (obs, reward, done, info)
obs, reward, done, info = env.step(action)

# render() visualizes state
env.render()

# close() cleans up
env.close()
```

---

## 🚀 Training

### Quick Start

```bash
# Install
pip install openenv-asr

# Train agent
python training/train_hybrid_agent.py \
    --episodes 100 \
    --lr 3e-4 \
    --device cuda

# Evaluate
python training/evaluate_agent.py \
    checkpoints/agent_ep100_reward500.pt \
    --scenarios 50 \
    --device cuda
```

### Training Output

```
🚀 Starting training on cuda
   Episodes: 100
   Learning Rate: 0.0003

Episode 10/100
  Reward: 150.45 (avg: 120.32)
  Length: 45 (avg: 42.3)
  Tests Passed: 3

Episode 20/100
  Reward: 275.60 (avg: 198.40)
  Length: 38 (avg: 39.1)
  Tests Passed: 4
...
```

### Custom Training

```python
from environment.gym_integration import ASREnvironmentHub, register_environments
from agents.hybrid_actor_critic_agent import HybridActorCriticAgent

register_environments()

env = ASREnvironmentHub(
    num_scenarios=500,    # 500 unique scenarios
    seed=42,              # Reproducible
    max_steps=100,
    human_in_the_loop=True
)

agent = HybridActorCriticAgent(
    input_dim=512,
    hidden_dim=256,
    learning_rate=3e-4,
    device='cuda'
)

# Your custom training loop
for episode in range(100):
    obs = env.reset()
    rewards = []
    done = False
    
    while not done:
        action, conf = agent.get_action(obs)
        obs, reward, done, info = env.step(action)
        rewards.append(reward)
    
    agent.update(rewards)
```

---

## 📊 Evaluation Metrics

### Success Rate

```python
success_rate = (num_episodes_all_tests_pass) / (total_episodes)
```

**Target**: > 80% success rate on unseen scenarios

### Average Tests Fixed

```python
avg_tests_fixed = mean([tests_passed for each episode])
```

**Target**: > 4/5 tests fixed

### Sample Efficiency

```python
reward_per_step = total_reward / episode_length
```

**Measures**: How efficiently agent explores

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│         Hugging Face Hub Integration                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │  Gymnasium API (gym-compatible)            │   │
│  └────────────────────────────────────────────┘   │
│                  ↓                                   │
│  ┌────────────────────────────────────────────┐   │
│  │   ASREnvironmentHub                        │   │
│  │   ├─ Dynamic Scenario Generator            │   │
│  │   ├─ 500+ unique scenarios                 │   │
│  │   └─ Reproducible seeding                  │   │
│  └────────────────────────────────────────────┘   │
│                  ↓                                   │
│  ┌─────────────────┬─────────────────┐            │
│  ↓                 ↓                 ↓              │
│ [Agent]       [Env]            [Generator]        │
│  ↓                 ↓                 ↓              │
│ [Hybrid        [Sandbox]      [Bug Templates]     │
│  Actor-        [File Ops]      [Pytest Runner]   │
│  Critic]       [AST Parser]                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Decoupling Benefits

- **Agent** can be swapped (DQN, A3C, etc.)
- **Environment** can use different backends
- **Generator** can create arbitrary scenarios
- **All** independently testable and deployable

---

## 🎯 Research Applications

### 1. Scalability Studies
- Train on different numbers of scenarios (10, 100, 500, 1000+)
- Measure generalization to unseen bugs

### 2. Agent Comparison
- Compare Hybrid Actor-Critic vs. DQN vs. Rule-based
- Benchmark on same diverse scenarios

### 3. Bug Pattern Analysis
- Which bugs are hardest to fix?
- Which agents excel at specific bug types?

### 4. Transfer Learning
- Pre-train on 100+ scenarios
- Fine-tune on domain-specific bugs (web frameworks, ML libraries)

---

## 📝 Citation

If you use this advanced environment in research:

```bibtex
@software{openenv_asr_advanced_2026,
  title={OpenEnv: Hybrid Actor-Critic for Automated Software Repair},
  author={Your Name},
  year={2026},
  url={https://github.com/YOUR-USERNAME/openenv-asr}
}
```

---

## 🔗 Links

- [Gymnasium Documentation](https://gymnasium.farama.org/)
- [Hugging Face Hub](https://huggingface.co/)
- [PPO Paper](https://arxiv.org/abs/1707.06347)
- [Tree-sitter](https://tree-sitter.github.io/)

---

**Hub-ready** ✅ | **500+ scenarios** ✅ | **Transformer-based** ✅ | **pip install ready** ✅