# Aurora ASR: The Self-Healing CI/CD Agent 🚀

**Aurora** is an advanced, RL-powered Automated Software Repair (ASR) system designed to identify, analyze, and repair code bugs autonomously within your CI/CD pipeline.

## 🎯 The Vision
Modern developers spend up to 30% of their time debugging trivial errors (off-by-one, operator flips, null references). **Aurora** aims to recover that time by living in your GitHub Actions, catching failing tests, and proposing high-confidence AST-aware patches before you even notice.

## 📺 Interactive Demo
We've included a high-impact visual demo to showcase Aurora's reasoning in real-time.
```bash
# Run the Aurora Repair Pipeline Visualization
python hackathon_demo.py
```

Perfect for research in:
- Automated Program Repair (APR)
- Code Generation with RL
- Self-Healing Systems
- Bug Localization

## ⚙️ Features

### ✅ Sandboxed Execution
- Dockerized sandbox prevents host machine access
- Isolated file system per episode
- Subprocess execution with timeouts
- Resource limits (memory, CPU)

### 🎮 Action Space
```python
- read_file(path: str) → str
- write_file(path: str, content: str) → bool
- run_pytest() → {"stdout": str, "stderr": str, "returncode": int}
```

### 👁️ Observation Space
```python
{
    "file_tree": str,           # Current directory structure
    "current_file": str,        # Content of 'watched' file
    "last_output": str,         # Last 100 lines of terminal output
    "parse_tree": dict,         # Tree-sitter AST representation
    "test_results": dict,       # Last test run results
}
```

### 🏆 Reward Logic
```
+50 per test: Fail → Pass
+200: All tests pass
-100: SyntaxError introduced
-10: Illegal file operation (e.g., accessing /etc/)
+5: Asking for human feedback when 90% uncertain (optional)
```

### 🛡️ Safety Features
- File I/O sandboxing (whitelist: `src/`, `tests/` only)
- Syntax validation via AST parsing
- Memory/timeout limits
- Human-in-the-loop approval for risky operations

### 🌳 Tree-Sitter Integration
The agent sees code as **parsed syntax trees**, not raw text:
```python
{
    "node_type": "function_definition",
    "name": "calculate_sum",
    "parameters": [...],
    "body": {...},
}
```

## 🚀 Quick Start

### Installation
```bash
# Clone and install
git clone https://github.com/YOUR-USERNAME/openenv-asr.git
cd openenv-asr
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

### Simple Example
```python
from environment.asr_env import ASREnvironment

# Initialize environment
env = ASREnvironment(
    repo_template="sample_buggy_code",
    num_tests=5,
    docker_image="openenv-asr:latest"
)

# Reset for new episode
obs = env.reset()

# Agent takes action
obs, reward, done, info = env.step(
    action="read_file",
    params={"path": "src/calculator.py"}
)

# Check observations
print(obs["file_tree"])
print(obs["current_file"])
print(obs["parse_tree"])
```

## 📦 Environment Structure

### Per-Episode Sandbox
```
/tmp/episode_<id>/
├── src/
│   ├── calculator.py          (buggy code)
│   └── utils.py
├── tests/
│   ├── test_basic.py          (5 test files)
│   ├── test_edge_cases.py
│   └── ...
├── .gitignore
└── pytest.ini
```

### Initialization
1. **Copy template** buggy repo to `/tmp/episode_<id>/`
2. **Run pytest** to identify failing tests
3. **Parse AST** via Tree-sitter for initial observation
4. **Yield initial obs** with file tree, parse trees, and test results

## 🤖 Training an Agent

```python
from environment.asr_env import ASREnvironment
from agents.example_repair_agent import RepairAgent

env = ASREnvironment(num_tests=5)
agent = RepairAgent(
    use_tree_sitter=True,
    human_in_the_loop_threshold=0.9
)

for episode in range(100):
    obs = env.reset()
    done = False
    total_reward = 0
    
    while not done:
        action, confidence = agent.get_action(obs)
        
        # Human approval for uncertain, risky actions
        if confidence < 0.9 and action in ["write_file", "modify_config"]:
            approval = input(f"Approve action? {action} (y/n): ")
            if approval != "y":
                reward = 5  # Small reward for asking
                continue
        
        obs, reward, done, info = env.step(action, info["params"])
        total_reward += reward
    
    print(f"Episode {episode}: Total reward = {total_reward}")
```

## 🏗️ Architecture

### Core Components

#### `ASREnvironment` (Gym-compatible)
- Manages episodes, resets, steps
- Handles sandbox creation/cleanup
- Orchestrates Docker execution

#### `Sandbox` 
- Dockerized Python execution
- File system isolation
- Timeout/resource management

#### `ObservationSpace`
- Builds file tree representation
- Extracts current file content
- Parses AST via Tree-sitter
- Formats terminal output history

#### `ActionSpace`
- Validates actions (type, parameters)
- Executes read/write/run_pytest
- Checks sandbox constraints

#### `RewardLogic`
- Tracks test state changes
- Detects syntax errors
- Awards human-in-the-loop bonus
- Provides step rewards

#### `TreeSitterParser`
- Parses Python AST
- Converts to JSON representation
- Identifies function/class definitions
- Extracts variable assignments

## 📊 Observation Example

```json
{
    "file_tree": "src/\n  ├── calculator.py\n  └── utils.py\ntests/\n  └── test_calculator.py",
    "current_file": "def add(a, b):\n    return a + b + c  # Bug: 'c' undefined",
    "parse_tree": {
        "type": "module",
        "body": [
            {
                "type": "function_def",
                "name": "add",
                "parameters": ["a", "b"],
                "body": [...],
                "errors": ["NameError: name 'c' is not defined"]
            }
        ]
    },
    "test_results": {
        "passed": 2,
        "failed": 3,
        "details": [
            {"test": "test_add_basic", "status": "PASS"},
            {"test": "test_add_negative", "status": "FAIL", "error": "NameError"}
        ]
    },
    "last_output": "... last 100 lines of pytest output ..."
}
```

## 🔒 Safety & Sandboxing

### File Operation Whitelist
```python
ALLOWED_PATHS = [
    "/tmp/episode_<id>/src/**/*.py",
    "/tmp/episode_<id>/tests/**/*.py",
]
```

### Prevented Operations
- ❌ Deleting test files
- ❌ Writing outside `src/` and `tests/`
- ❌ Modifying system files
- ❌ Running arbitrary commands
- ❌ Creating symlinks to `/etc/`, `/home/`, etc.

### Execution Controls
- Subprocess timeout: 30 seconds
- Memory limit: 512MB
- CPU limit: 1 core
- Network: Disabled

## 👤 Human-in-the-Loop

Enable human feedback for uncertain decisions:

```python
env = ASREnvironment(human_in_the_loop=True)

action, confidence = agent.get_action(obs)

if confidence < 0.9:
    # Agent asks for help
    print(f"Agent confidence: {confidence:.2%}")
    print(f"Proposed action: {action}")
    human_choice = input("Approve? (y/n): ")
    reward += 5 if human_choice == "y" else -5
```

## 🌳 Tree-Sitter Capabilities

Parse Python code into structured AST:

```python
from environment.tree_sitter_parser import TreeSitterParser

parser = TreeSitterParser()
tree = parser.parse("def foo(x): return x + 1")

print(tree)
# Output: {
#   "type": "module",
#   "functions": [
#       {
#           "name": "foo",
#           "params": ["x"],
#           "returns": "x + 1"
#       }
#   ]
# }
```

## 📝 Customization

### Create Custom Buggy Repos

1. Create `repos/my_buggy_code/`:
```
my_buggy_code/
├── src/
│   └── main.py
├── tests/
│   └── test_main.py
└── pytest.ini
```

2. Register in environment:
```python
env = ASREnvironment(repo_template="my_buggy_code")
```

### Extend Reward Function

```python
from environment.reward_logic import RewardLogic

class CustomRewardLogic(RewardLogic):
    def compute_reward(self, prev_results, curr_results):
        reward = super().compute_reward(prev_results, curr_results)
        
        # Add custom bonus for code coverage
        if curr_results["coverage"] > prev_results["coverage"]:
            reward += 25
        
        return reward
```

## 🧪 Testing

```bash
pytest tests/
pytest tests/test_integration.py -v
```

## 📚 References

- [OpenAI Gym Documentation](https://gym.openai.com/)
- [Tree-sitter Python Bindings](https://github.com/tree-sitter/py-tree-sitter)
- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - See LICENSE file

## 🎓 Citation

If you use this environment in research, please cite:

```bibtex
@software{openenv_asr_2026,
  title={OpenEnv: Automated Software Repair Environment},
  author={Your Name},
  year={2026},
  url={https://github.com/YOUR-USERNAME/openenv-asr}
}
```

---

**Hub-ready**: `pip install openenv-asr` - Train agents anywhere! 🚀