# src/layers/perception/perception_layer.py
from typing import Dict, Any
import logging
from ..base_layer import BaseLayer
from .text_processor import TextProcessor
from .context_analyzer import ContextAnalyzer
from .semantic_mapper import SemanticMapper

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
        return context_analysis.overall_confidence

# src/layers/base_layer.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLayer(ABC):
    def __init__(self, name: str, message_bus, config: Dict[str, Any]):
        self.name = name
        self.message_bus = message_bus
        self.config = config
        
    @abstractmethod
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Основная функция обработки слоя"""
        pass
        
    def shutdown(self):
        """Корректное завершение работы слоя"""
        pass