"""Canonical public import surface for AI Automation Force core contracts.

The underlying `lullabies_core` module remains temporarily available as a compatibility
namespace for pre-M01 repository code. New consumers should import this package.
"""

from lullabies_core import *  # noqa: F403
from lullabies_core import __all__ as __all__
