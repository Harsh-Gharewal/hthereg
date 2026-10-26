"""Entrypoint for Vercel / serverless deployments of the backend service."""
import sys
import types
from pathlib import Path

# Ensure backend directory and its parent are in sys.path
backend_dir = Path(__file__).resolve().parent
root_dir = backend_dir.parent

for p in (backend_dir, root_dir):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# When deployed on Vercel with root="backend", the service root is backend_dir itself,
# so the parent directory does not contain a "backend" package.
# Register a virtual "backend" module pointing to backend_dir so that
# all existing "from backend.app..." imports resolve cleanly without changes!
if "backend" not in sys.modules:
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(backend_dir)]
    backend_pkg.__file__ = str(backend_dir / "__init__.py")
    sys.modules["backend"] = backend_pkg

from backend.app.main import app  # noqa: E402, F401
