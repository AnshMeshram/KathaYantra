"""Diagnostic CLI Script to Check Ollama Status and Configured Models.

Inspects the local Ollama instance and reports whether the configured Gemma 2 model
is ready for inference without executing a heavy generation prompt.
"""

import asyncio
from pathlib import Path
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.ollama_client import ollama_client


async def main():
    print("=" * 70)
    print("  KATHAYANTRA — LOCAL OLLAMA SERVICE DIAGNOSTICS")
    print("=" * 70)
    health = await ollama_client.check_health()
    print(f"Status:            {health.status.upper()}")
    print(f"Provider:          {health.provider}")
    print(f"Endpoint:          {health.base_url}")
    print(f"Configured Model:  {health.configured_model}")
    print(f"Model Ready:       {'YES' if health.model_available else 'NO'}")
    print(f"Installed Models:  {', '.join(health.installed_models) if health.installed_models else 'None'}")
    print("-" * 70)
    print(f"Message: {health.message}")
    print("=" * 70)
    if not health.model_available:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

