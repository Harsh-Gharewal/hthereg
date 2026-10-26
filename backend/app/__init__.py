"""Day-Ahead Wind Forecast Backend Application."""

import sys
import types
from pathlib import Path

# When deployed in an isolated backend container, ensure 'backend' is resolved
if "backend" not in sys.modules:
    backend_dir = Path(__file__).resolve().parent.parent
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(backend_dir)]
    backend_pkg.__file__ = str(backend_dir / "__init__.py")
    sys.modules["backend"] = backend_pkg

__version__ = "0.1.0"
