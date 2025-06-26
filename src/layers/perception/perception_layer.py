# src/layers/perception_layer.py
from typing import Dict, Any
import logging

try:
    from ..base_layer import BaseLayer
except ImportError:
    # Если base_layer не найден, создаем простую заглушку
    class BaseLayer:
        def __init__(self, name: str, message_bus, config: Dict[str, Any]):
            self.name = name
            self.message_bus = message_bus
            self.config = config
        
        def process(self, input_data: Any) -> Dict[str, Any]:
            pass
        
        def shutdown(self):
            pass

try:
    from text_processor import TextProcessor
    from context_analyzer import ContextAnalyzer  
    from semantic_mapper import SemanticMapper
except ImportError:
    # Заглушки для недостающих модулей
    class TextProcessor:
        def __init__(self, config=None):
            pass
        def process(self, text):
            return type('ProcessedText', (), {
                'original': text,
                'language': 'en',
                'tokens': [],
                'entities': [],
                'sentences': [text],
                'keywords': [],
                'sentiment': 0.0,
                'complexity': 0.5
            })()
    
    class ContextAnalyzer:
        def __init__(self, config=None):
            pass
        def analyze(self, processed_text):
            return type('ContextAnalysis', (), {
                'levels': [],
                'overall_confidence': 0.5,
                'primary_intent': 'unknown',
                'emotional_tone': 'neutral',
                'complexity_level': 'medium'
            })()
    
    class SemanticMapper:
        def __init__(self, config=None):
            pass
        def create_map(self, processed_text, context_analysis):
            return type('SemanticMap', (), {
                'concepts': [],
                'relationships': [],
                'abstraction_levels': {0: [], 1: [], 2: []},
                'semantic_vector': [],
                'complexity_score': 0.5
            })()

class PerceptionLayer(BaseLayer):
    def __init__(self, message_bus, config: Dict[str, Any]):
        super().__init__("perception", message_bus, config)
        
        self.text_processor = TextProcessor(config.get('text_processor', {}))
        self.context_analyzer = ContextAnalyzer(config.get('context_analyzer', {}))
        self.semantic_mapper = SemanticMapper(config.get('semantic_mapper', {}))
        
        self.logger = logging.getLogger(__name__)
        
    def process(self, input_data: str) -> Dict[str, Any]:
        """Основная обработка в слое восприятия"""
        try:
            # Этап 1: Обработка текста
            processed_text = self.text_processor.process(input_data)
            
            # Этап 2: Анализ контекста
            context_analysis = self.context_analyzer.analyze(processed_text)
            
            # Этап 3: Семантическое картирование
            semantic_map = self.semantic_mapper.create_map(processed_text, context_analysis)
            
            # Формирование результата
            result = {
                'processed_text': processed_text,
                'context_analysis': context_analysis,
                'semantic_map': semantic_map,
                'perception_confidence': self._calculate_overall_confidence(context_analysis),
                'processing_metadata': {
                    'layer': 'perception',
                    'input_length': len(input_data),
                    'concepts_extracted': len(semantic_map.concepts),
                    'relationships_found': len(semantic_map.relationships)
                }
            }
            
            self.logger.info(f"Perception processing completed. Confidence: {result['perception_confidence']:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in perception layer: {e}")
            return {
                'error': str(e),
                'perception_confidence': 0.0
            }
            
    def _calculate_overall_confidence(self, context_analysis) -> float:
        """Расчет общей уверенности слоя восприятия"""
        try:
            return context_analysis.overall_confidence
        except:
            return 0.5  # Значение по умолчанию