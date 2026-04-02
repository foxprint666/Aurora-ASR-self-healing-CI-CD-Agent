# Aurora ASR: The Self-Healing CI/CD Agent 🚀

**Aurora ASR** is a high-performance, **OpenEnv-v4 compliant** Automated Software Repair system. It leverages Reinforcement Learning and Large Language Models (LLMs) to autonomously detect and repair software bugs within isolated sandboxes.

## 🌟 Features
- **OpenEnv-v4 Compliant**: Fully compatible with the Meta PyTorch Hackathon automated judging system (`[OK] : Ready for multi-mode deployment`).
- **Typed API**: Uses strict Pydantic models for **Observations**, **Actions**, and **Rewards**.
- **3-Tier Task System**: Includes Easy (Typo), Medium (Logic), and Hard (Edge Case) repair challenges.
- **Smart Fallback (Mock Mode)**: Automatically switches to a scripted **Mock Agent** if no API key is provided, allowing for offline demos and testing.
- **Structured Logging**: Emits `[START]`, `[STEP]`, and `[END]` tags for real-time progress tracking and grading.
- **Dockerized Sandboxing**: Safe execution of agent-generated code with resource limits.

## 🛠️ Installation
Using the Python Launcher for Windows (`py`):
```cmd
# Install core dependencies
py -m pip install -r requirements.txt

# Install the OpenEnv core library
py -m pip install openenv-core
```

## 🎮 Running the Agent
Aurora uses `inference.py` as its primary execution entrypoint. It utilizes the OpenAI client to iterate through the 3 task tiers.

```cmd
# Option A: Real LLM Mode (requires OpenAI API Key)
set OPENAI_API_KEY=sk-your-key-here
py inference.py

# Option B: Mock Demo Mode (no key required)
set OPENAI_API_KEY=mock
py inference.py
```

> [!NOTE]
> Aurora will automatically detect if `OPENAI_API_KEY` is missing or invalid and fall back to the **Mock Agent**. To switch back to the real LLM, simply provide a valid API key in your environment variables.


## 🌳 Pydantic API Spec
Aurora adheres to the strict OpenEnv-v4 data schemas:

### Observation (`ASRObservation`)
```python
{
    "file_tree": "...",      # Directory structure
    "current_file": "...",   # Content with line numbers
    "test_results": {...},    # Pytest summary
    "reward": 0.0,           # Scalar reward
    "asr_reward": {...},      # Detailed Pydantic Reward Model
    "done": False            # Termination flag
}
```

### Action (`ASRAction`)
```python
{
    "command": "read_file",  # Options: read_file, write_file, run_pytest
    "params": {"path": "..."}
}
```

## 📊 Task Tiers
1. **Easy (`tasks/easy`)**: Fix a simple `NameError` (undefined variable).
2. **Medium (`tasks/medium`)**: Repair an off-by-one error in a factorial implementation.
3. **Hard (`tasks/hard`)**: Address a `ZeroDivisionError` in a complex data processor.

## 🛡️ Validation
Verify the repository structure and compliance using the OpenEnv CLI:
```cmd
py -m openenv.cli validate .
```

## 🤝 Contributing
Contributions welcome! Please see [ARCHITECTURE.md](ARCHITECTURE.md) for deeper technical details.

## 📄 License
MIT License - See LICENSE file