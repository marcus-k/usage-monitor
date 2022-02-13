"""
Usage Monitor Package.

"""
from .version import __version__

from .monitor import (
    BufferTime,
    MonitorCPU,
    Runtime,
    _GPU,
)

if _GPU:
    from .monitor import MonitorGPU