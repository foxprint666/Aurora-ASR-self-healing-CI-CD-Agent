# Contributing to OpenEnv ASR

Thank you for your interest in contributing! This document provides guidelines and instructions.

---

## 🎯 Code of Conduct

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on the code, not the person
- Help others learn and grow

---

## 🚀 Getting Started

### Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/openenv-asr.git
cd openenv-asr
git remote add upstream https://github.com/23444555323/openenv-asr.git
```

### Create Development Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

---

## 📝 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Edit files, add features, fix bugs

# Run tests
pytest tests/ -v

# Format code
black environment agents training tests

# Lint
flake8 environment agents training tests

# Type check
mypy environment agents training
```

### 3. Commit and Push

```bash
git add .
git commit -m "feat: Add new feature"
git push origin feature/my-feature
```

### 4. Create Pull Request

- Clear description of changes
- Reference related issues (#123)
- Include tests for new code
- Update documentation

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_advanced_components.py::TestScenarioGenerator -v

# With coverage
pytest tests/ --cov=environment --cov=agents --cov-report=html

# Watch mode (requires pytest-watch)
ptw tests/
```

### Write Tests

```python
# tests/test_my_feature.py
import unittest
from my_module import MyClass

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        self.obj = MyClass()
    
    def test_feature(self):
        result = self.obj.do_something()
        self.assertEqual(result, expected_value)
```

---

## 📚 Documentation

### Update README

- Explain new features clearly
- Add code examples
- Update Table of Contents if needed

### Add Docstrings

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something is wrong
        
    Example:
        >>> result = my_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

---

## 🔍 Code Style

### Black Formatting

```bash
# Format all code
black environment agents training tests

# Check without modifying
black --check environment agents training tests
```

### Naming Conventions

```python
# Classes: PascalCase
class HybridActorCriticAgent:
    pass

# Functions/variables: snake_case
def train_agent(num_episodes: int):
    episode_rewards = []

# Constants: UPPER_SNAKE_CASE
MAX_STEPS = 1000
LEARNING_RATE = 3e-4
```

---

## 🐛 Bug Reports

### Report a Bug

1. **Search** existing issues first
2. **Title**: Brief, descriptive
3. **Description**: What happened, expected behavior
4. **Steps**: Reproduce the bug
5. **Environment**: Python version, OS, etc.
6. **Logs**: Error messages, stack traces

### Example

```
Title: Agent crashes on invalid observation

Description:
When training with certain scenarios, the agent crashes with:
  TypeError: unsupported operand type(s) for +: 'NoneType' and 'float'

Steps to Reproduce:
1. Generate 100 scenarios
2. Train agent for 10 episodes
3. Agent crashes on episode 7

Environment:
- Python 3.10
- Ubuntu 22.04
- CUDA 11.8
- PyTorch 2.0

Error Log:
[Full stack trace here]
```

---

## ✨ Feature Requests

### Suggest an Enhancement

1. **Title**: Clear feature description
2. **Problem**: What problem does this solve?
3. **Solution**: How should it work?
4. **Example**: Show desired usage

### Example

```
Title: Add DQN agent variant

Problem:
Currently only Hybrid Actor-Critic is supported. Having alternative
algorithms would allow comparison and applicability to different tasks.

Solution:
Implement DQNAgent inheriting from BaseAgent with:
- Q-network architecture
- Experience replay buffer
- Target network updates

Example:
agent = DQNAgent(hidden_dim=256)
obs = env.reset()
action, confidence = agent.get_action(obs)
```

---

## 📋 Commit Messages

### Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Test addition/modification
- `ci`: CI/CD changes
- `chore`: Maintenance

### Example

```
feat: Add DQN agent implementation

Implement DQN agent with experience replay and target networks.
Inherits from BaseAgent for compatibility with ASR environment.

Closes #42
```

---

## 🎓 Learning Resources

- [Gymnasium Docs](https://gymnasium.farama.org/)
- [PyTorch Docs](https://pytorch.org/docs/)
- [PPO Paper](https://arxiv.org/abs/1707.06347)
- [Clean Code Best Practices](https://google.github.io/styleguide/pyguide.html)

---

## 🙏 Thank You!

Your contributions make this project better for everyone. Whether it's code, documentation, bug reports, or feature suggestions, we appreciate your involvement!

For questions, reach out on GitHub Discussions or open an issue.

**Happy contributing!** 🚀