# Ethical Memory Structure (EMS) Gateway

A self-regulating ethical gateway that sits in front of an LLM, evaluates prompts,
tracks value drift, adjusts posture, and explains its own decisions.

## Features

- Core ethical layers:
  - CoreValuesLayer
  - ContextualEthicsLayer
  - RelationalIdentityLayer
  - ValueTensionAnalyzer
- Ethical load + value drift tracking
- Meta-controller posture regulation (NOMINAL / CAUTIOUS / HARDENED)
- ASCII sparkline telemetry and policy evolution tracking
- Guarded LLM wrapper (BLOCK / ALLOW / MODIFY)
- REST API via FastAPI
- CLI runner
- Pluggable LLM providers

## Project Layout

```text
ems_project/
├── engine.py
├── ems_agent.py
├── guarded_llm.py
├── config_loader.py
├── logger.py
├── api.py
├── main.py
├── llm_providers.py
├── tests/
│   └── test_ems.py
├── config/
│   └── config.json
└── logs/
    └── ems.log

