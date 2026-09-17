"""Vynk Backend Application Package."""
import os
import sys

# Ensure backend directory is in sys.path so 'app.*' imports resolve from root or any working directory
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

__version__ = "0.1.0"

