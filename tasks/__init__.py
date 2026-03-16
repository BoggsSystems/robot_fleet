# High-level task definitions for warehouse, retail, and manufacturing.
# AI extension point: New task modules can be generated from prompts and imported here.

from .inventory_scan import run_inventory_scan
from .restock import run_restock

__all__ = ["run_inventory_scan", "run_restock"]
