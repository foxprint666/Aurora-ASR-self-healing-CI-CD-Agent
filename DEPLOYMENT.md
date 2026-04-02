# Aurora ASR - Deployment Guide

This guide covers the deployment of the **Aurora ASR** self-healing agent in OpenEnv-v4 compliant environments.

---

## 🚀 Local Development

### Requirements
- Python 3.8+
- Git
- Docker (for sandbox isolation)
- OpenAI API Key

### Setup & Installation
Using the Python Launcher for Windows (`py`):

```cmd
# 1. Clone the repository
git clone https://github.com/foxprint666/Aurora-ASR-self-healing-CI-CD-Agent.git
cd Aurora-ASR-self-healing-CI-CD-Agent

# 2. Install dependencies
py -m pip install -r requirements.txt

# 3. Install OpenEnv core
py -m pip install openenv-core
```

### Running Inference
Aurora uses a centralized `inference.py` script to evaluate the 3 task tiers.

```cmd
# Set your API key
set OPENAI_API_KEY=sk-your-key-here

# Run the agent
py inference.py
```

---

## 🐳 Docker Deployment

The `Dockerfile` in the root directory is optimized for OpenEnv-v4.

### Build Image
```cmd
docker build -t aurora-asr:v1 .
```

### Run Container
```cmd
docker run -it -e OPENAI_API_KEY=sk-xxx aurora-asr:v1
```

---

## ☁️ Hugging Face Spaces

Aurora ASR is designed to be hosted as a **Hugging Face Space** with the `openenv` tag.

1. Create a New Space (Docker or Gradio).
2. Add your `OPENAI_API_KEY` as a Secret in the Space settings.
3. Push the repository content to the Space.
4. Ensure `openenv.yaml` is in the root directory for automated discovery.

---

## 🛡️ Validation & Grading

The Meta PyTorch Hackathon uses the `openenv` CLI to validate submissions.

```cmd
# Run validation locally
py -m openenv.cli validate .

# Output:
# [OK] : Ready for multi-mode deployment
```

### 🤖 Testing Without Keys (Mock Mode)
If you are presenting in an environment without internet or API credits, simply leave the `OPENAI_API_KEY` unset or set it to `mock`. Aurora will switch to a **Hard-coded Mock Agent** that demonstrates the repair flow for all 3 tasks (Easy, Medium, Hard).

---

## 🏗️ CI/CD Integration (GitHub Actions)

Aurora can be triggered as a GitHub Action to repair failing tests automatically.

```yaml
jobs:
  repair:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Aurora
        run: |
          pip install -r requirements.txt
          pip install openenv-core
          python inference.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```
