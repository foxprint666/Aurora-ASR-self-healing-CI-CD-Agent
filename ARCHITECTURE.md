# Aurora ASR - OpenEnv-v4 Architecture Documentation

## 📐 System Overview

Aurora ASR implements the **OpenEnv-v4** specification for autonomous software repair. It utilizes a strict Pydantic-based messaging system to ensure type-safe interactions between the Agent and the Repair Environment.

```
┌─────────────────────────────────────────────────────────────┐
│                    Aurora ASR Agent (LLM)                   │
└─────────────────────────────────────────────────────────────┘
                             ↓ 
            [Action: ASRAction (Pydantic)]
            (Fallback to Mock Agent if API fails)
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    OpenEnv-v4 Server Engine                 │
│  ├─ Environment: inherits openenv.core.Environment           │
│  ├─ API: reset(), step(), state (property)                  │
│  ├─ Packaging: pyproject.toml, server/app.py, uv.lock        │
│  └─ Logic: RewardLogic, ActionSpace, ObservationSpace        │
└─────────────────────────────────────────────────────────────┐
                             ↓
            [Observation: ASRObservation (Pydantic)]
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    Isolated Sandbox (Docker)                │
│  ├─ ephemeral environment                                   │
│  ├─ read/write whitelisting                                 │
│  └─ pytest automated grader                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ Core Components (OpenEnv-v4)

### 1. Pydantic Modeling Layer (`environment/models.py`)
Aurora uses Pydantic to enforce the OpenEnv-v4 data contracts.

- **`ASRAction`**: Inherits from `openenv.core.env_server.types.Action`.
  - `command`: `read_file`, `write_file`, `run_pytest`.
  - `params`: JSON object with command parameters (e.g., `path`, `content`).
- **`ASRObservation`**: Inherits from `openenv.core.env_server.types.Observation`.
  - Core fields: `file_tree`, `current_file`, `test_results`, `parse_tree`, `last_output`.
  - **`asr_reward`**: A specialized `ASRReward` Pydantic model for granular scoring.
- **`ASRState`**: Inherits from `openenv.core.env_server.types.State`.
  - Internal metadata: `episode_id`, `step_count`, `current_file`, `last_test_results`.

### 2. Environment Layer (`environment/asr_env.py`)
The environment is the core orchestrator, inheriting from `openenv.core.env_server.interfaces.Environment`.

- **`reset()`**: Initializes a new sandbox for a specific task tier (Easy, Medium, Hard).
- **`step()`**: Executes an action and returns the resulting **Observation** model, including the reward and done flag.
- **`state`**: A property that returns the full **State** model for introspection by the grader.

### 3. Task Management (`tasks/`)
Each task is a standalone repository with a buggy source and a suite of passing/failing tests.

- **Easy**: `tasks/easy` (NameError repair).
- **Medium**: `tasks/medium` (Off-by-one logic fix).
- **Hard**: `tasks/hard` (ZeroDivisionError edge case).

## 🚀 Execution Flow

### Inference Pipeline (`inference.py`)
1. **[START] Tag**: Signal the beginning of a task evaluation.
2. **LLM Loop**: Agent receives `ASRObservation` and emits an `ASRAction`.
   - **Automatic Fallback**: If no OpenAI/Gemini API key is detected, the agent triggers `get_mock_action()`, a scripted reasoning engine that demonstrates the system's repair capabilities natively.
3. **Sandbox Execution**: Code is written and tests are run in the isolated environment.
4. **[STEP] Tag**: Log action results and the incremental reward.
5. **[END] Tag**: Emitted when all tests pass (Success) or the step limit is reached (Failure).

## 🛡️ Security & Isolation
- **Sandboxing**: Docker containers provide process and filesystem isolation.
- **AST Parsing**: Tree-sitter is used to validate that agent-generated code is syntactically valid before it is written to the source.

## 📊 Compliance Checklist
- [x] Pydantic models for Action, Observation, Reward.
- [x] Standard `reset()`, `step()`, `state` endpoints.
- [x] `openenv.yaml` metadata definition.
- [x] Structured stdout logging for automated graders.