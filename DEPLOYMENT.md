# OpenEnv ASR - Deployment Guide

Complete guide for deploying OpenEnv ASR in various environments.

---

## 🚀 Local Development

### Requirements
- Python 3.8+
- Git
- Docker (optional)
- CUDA 11.0+ (optional, for GPU)

### Setup

```bash
# Clone repository
git clone https://github.com/23444555323/openenv-asr.git
cd openenv-asr

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run tests
pytest tests/ -v

# Start training
python training/train_hybrid_agent.py --episodes 100 --device cpu
```

---

## 🐳 Docker Deployment

### Build Image

```bash
# Build Docker image
docker build -t openenv-asr:latest .

# Tag for Docker Hub
docker tag openenv-asr:latest YOUR_USERNAME/openenv-asr:latest
```

### Run Container

```bash
# CPU
docker run -it openenv-asr:latest python training/train_hybrid_agent.py

# GPU
docker run --gpus all -it openenv-asr:latest python training/train_hybrid_agent.py

# With mounted volumes
docker run -it \
  -v $(pwd)/checkpoints:/app/checkpoints \
  -v $(pwd)/notebooks:/app/notebooks \
  openenv-asr:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up

# Training only
docker-compose up asr-train

# Jupyter notebook
docker-compose up jupyter
# Access at http://localhost:8888
```

---

## ☁️ Cloud Deployment

### AWS EC2

```bash
# Launch GPU instance (p3.2xlarge)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type p3.2xlarge \
  --key-name your-key

# SSH into instance
ssh -i your-key.pem ubuntu@<instance-ip>

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Pull and run
sudo docker pull YOUR_USERNAME/openenv-asr:latest
sudo docker run --gpus all -it YOUR_USERNAME/openenv-asr:latest
```

### Google Cloud (Vertex AI)

```bash
# Create custom training job
gcloud ai custom-jobs create \
  --display-name="openenv-asr-training" \
  --config=training_config.yaml

# Content of training_config.yaml:
displayName: "openenv-asr-training"
jobSpec:
  workerPoolSpecs:
    - machineSpec:
        machineType: n1-standard-8
        acceleratorType: NVIDIA_TESLA_V100
        acceleratorCount: 1
      replicaCount: 1
      containerSpec:
        imageUri: gcr.io/YOUR_PROJECT/openenv-asr:latest
        command:
          - python
          - training/train_hybrid_agent.py
          - --episodes
          - "1000"
```

### Hugging Face Spaces

```bash
# Create Space on Hugging Face
# Then push code:

git clone https://huggingface.co/spaces/YOUR_USERNAME/openenv-asr
cd openenv-asr

# Copy files
cp -r /path/to/openenv-asr/* .

# Create requirements.txt
pip freeze > requirements.txt

# Create app.py for Gradio interface
cat > app.py << 'EOF'
import gradio as gr
from environment.gym_integration import ASREnvironmentHub
from agents.hybrid_actor_critic_agent import HybridActorCriticAgent

def train_agent():
    # Training logic here
    return "Training started..."

interface = gr.Interface(
    fn=train_agent,
    inputs=[],
    outputs="text"
)

interface.launch()
EOF

# Push
git add .
git commit -m "Deploy to Hugging Face Spaces"
git push
```

---

## 📦 PyPI Installation

### From PyPI

```bash
# Install from PyPI
pip install openenv-asr

# Verify installation
python -c "from environment.asr_env import ASREnvironment; print('✅ Installed')"

# Run example
python -c "
from environment.gym_integration import ASREnvironmentHub
env = ASREnvironmentHub()
obs = env.reset()
print('✅ Environment ready')
"
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

All workflows are in `.github/workflows/`:
- `ci.yml`: Run tests on every push
- `release.yml`: Publish to PyPI on tag
- `docker-hub.yml`: Push to Docker Hub
- `publish-hub.yml`: Publish to Hugging Face Hub

### Trigger Releases

```bash
# Create tag
git tag v0.2.0

# Push tag (triggers CI/CD)
git push origin v0.2.0

# This will:
# 1. Run tests
# 2. Build distribution
# 3. Publish to PyPI
# 4. Build and push Docker image
# 5. Upload to Hugging Face Hub
```

---

## 📊 Monitoring

### TensorBoard

```bash
# Start training with TensorBoard
python training/train_hybrid_agent.py \
  --episodes 1000 \
  --tensorboard-dir ./logs

# View dashboard
tensorboard --logdir ./logs
# Access at http://localhost:6006
```

### Weights & Biases

```python
import wandb
from training.train_hybrid_agent import Trainer

# Initialize W&B
wandb.init(project="openenv-asr")

# Training with W&B logging
trainer = Trainer(num_episodes=1000)
trainer.train()  # Automatically logs to W&B
```

### MLflow

```python
import mlflow
from training.train_hybrid_agent import Trainer

mlflow.start_run()
mlflow.set_experiment("openenv-asr")

trainer = Trainer(num_episodes=1000)
trainer.train()

mlflow.log_metrics({
    "best_reward": trainer.best_reward,
    "avg_reward": sum(trainer.episode_rewards) / len(trainer.episode_rewards),
})

mlflow.end_run()
```

---

## 🔐 Security Checklist

- [ ] Use environment variables for secrets (API tokens, credentials)
- [ ] Don't commit `.env` files
- [ ] Set up branch protection rules
- [ ] Enable CODEOWNERS for code review
- [ ] Use semantic versioning for releases
- [ ] Sign commits with GPG
- [ ] Keep dependencies updated
- [ ] Run security scans (bandit, safety)

```bash
# Security checks
pip install bandit safety
bandit -r environment agents training
safety check
```

---

## 📈 Scaling

### Multi-GPU Training

```python
import torch.nn as nn
from torch.nn.parallel import DataParallel

# Wrap agent for multi-GPU
agent = HybridActorCriticAgent()
agent.policy_net = DataParallel(agent.policy_net)
agent.value_net = DataParallel(agent.value_net)
```

### Distributed Training (Ray)

```python
import ray
from training.train_hybrid_agent import Trainer

ray.init()

# Distribute training across multiple nodes
@ray.remote
def train_agent_on_node(config):
    trainer = Trainer(**config)
    trainer.train()
    return trainer.best_reward

configs = [{"num_episodes": 100} for _ in range(4)]
results = ray.get([train_agent_on_node.remote(cfg) for cfg in configs])
```

---

## 🐛 Troubleshooting

### CUDA Out of Memory
```python
# Reduce batch size
agent = HybridActorCriticAgent(hidden_dim=128)  # Default: 256

# Or use CPU
agent = HybridActorCriticAgent(device='cpu')
```

### Slow Training
```bash
# Profile training
python -m cProfile -s cumtime training/train_hybrid_agent.py

# Use GPU
python training/train_hybrid_agent.py --device cuda

# Parallel scenarios
export OMP_NUM_THREADS=8
```

### Docker Issues
```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker build --no-cache -t openenv-asr:latest .
```

---

## 📞 Support

- GitHub Issues: [github.com/23444555323/openenv-asr/issues](https://github.com/23444555323/openenv-asr/issues)
- Discussions: [github.com/23444555323/openenv-asr/discussions](https://github.com/23444555323/openenv-asr/discussions)
- Email: your.email@example.com
