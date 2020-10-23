__all__ = ["console"]

__version__ = "0.0.5"

from rich.console import Console

from coinflip import _patch_dataclasses_json

console = Console()
