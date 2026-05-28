"""Compatibility wrapper for older imports.

The dashboard now keeps chart builders in :mod:`src.charts`.
"""

from .charts import *  # noqa: F401,F403
