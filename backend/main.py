"""Entrypoint for Vercel / serverless deployments of the backend service."""
import sys
from pathlib import Path

# Ensure repository root and backend directory are in sys.path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = Path(__file__).resolve().parent

for p in (root_dir, backend_dir):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app.main import app  # noqa: E402, F401
