# src/layers/__init__.py
try:
    from .perception_layer import PerceptionLayer
except ImportError:
    PerceptionLayer = None

try:
    from .memory.memory_layer import MemoryLayer
except ImportError:
    MemoryLayer = None

try:
    from .base_layer import BaseLayer
except ImportError:
    BaseLayer = None

# Экспортируем доступные классы
__all__ = []
if BaseLayer:
    __all__.append('BaseLayer')
if PerceptionLayer:
    __all__.append('PerceptionLayer')
if MemoryLayer:
    __all__.append('MemoryLayer')