# src/layers/perception/__init__.py
try:
    from .text_processor import TextProcessor
except ImportError:
    TextProcessor = None

try:
    from .context_analyzer import ContextAnalyzer
except ImportError:
    ContextAnalyzer = None

try:
    from .semantic_mapper import SemanticMapper
except ImportError:
    SemanticMapper = None

# Импортируем PerceptionLayer из родительской директории
try:
    from perception_layer import PerceptionLayer
except ImportError:
    PerceptionLayer = None

__all__ = []
if TextProcessor:
    __all__.append('TextProcessor')
if ContextAnalyzer:
    __all__.append('ContextAnalyzer')
if SemanticMapper:
    __all__.append('SemanticMapper')
if PerceptionLayer:
    __all__.append('PerceptionLayer')