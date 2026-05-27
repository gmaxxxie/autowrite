"""AutoWriteO Agent Core — Settler, Composer, Planner, RuleEngine, Fingerprint"""

import os
import sys

_pkg_dir = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_pkg_dir)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

_symlink = os.path.join(_parent, "book_agent_core")
if not os.path.exists(_symlink):
    os.symlink(_pkg_dir, _symlink)

__version__ = "0.1.0"
