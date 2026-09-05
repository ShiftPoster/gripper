import importlib.metadata
from pathlib import Path

try:
    __version__ = importlib.metadata.version(Path(__file__).parent.name)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
