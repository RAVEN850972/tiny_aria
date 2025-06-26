# src/tests/test_cognitive_pipeline.py
import pytest
from unittest.mock import Mock, MagicMock
from src.cognitive_pipeline import CognitivePipeline

class TestCognitivePipeline:
    def test_pipeline_initialization(self):
        """Тест инициализации пайплайна"""
        
        mock_layers = {
            'perception': Mock(),
            'memory': Mock(),
            'reasoning': Mock()
        }
        
        pipeline = CognitivePipeline(mock_layers)
        
        assert pipeline.layers == mock_layers
        assert 'perception' in pipeline.processing_order
        assert 'memory' in pipeline.processing_order
        
    def test_layer_processing_order(self):
        """Тест правильного порядка обработки слоев"""
        
        processing_order = []
        
        def mock_process(layer_name):
            def process(input_data):
                processing_order.append(layer_name)
                return {'result': f'{layer_name}_processed', 'confidence': 0.8}
            return process
        
        mock_layers = {
            'perception': Mock(),
            'memory': Mock(),
            'reasoning': Mock(),
            'metacognition': Mock(),
            'ethics': Mock()
        }
        
        for layer_name, layer in mock_layers.items():
            layer.process = mock_process(layer_name)
            
        pipeline = CognitivePipeline(mock_layers)
        result = pipeline.process_input("test input")
        
        # Проверяем правильный порядок
        expected_order = ['perception', 'memory', 'reasoning', 'metacognition', 'ethics']
        assert processing_order == expected_order
        
    def test_error_recovery(self):
        """Тест восстановления после ошибок в слоях"""
        
        mock_layers = {
            'perception': Mock(),
            'memory': Mock(),
            'reasoning': Mock()
        }
        
        # Perception работает нормально
        mock_layers['perception'].process.return_value = {
            'result': 'perception_ok',
            'confidence': 0.8
        }
        
        # Memory выдает ошибку
        mock_layers['memory'].process.side_effect = Exception("Memory error")
        
        # Reasoning работает нормально
        mock_layers['reasoning'].process.return_value = {
            'result': 'reasoning_ok', 
            'confidence': 0.7
        }
        
        pipeline = CognitivePipeline(mock_layers)
        result = pipeline.process_input("test input")
        
        # Система должна продолжить работу несмотря на ошибку в memory
        assert 'response' in result
        assert 'layer_results' in result
        assert 'perception' in result['layer_results']
        assert 'reasoning' in result['layer_results']
        
        # Проверяем, что ошибка зафиксирована в метаданных
        memory_metadata = None
        for layer_detail in result['processing_metadata']['layer_details']:
            if layer_detail.layer_name == 'memory':
                memory_metadata = layer_detail
                break
                
        assert memory_metadata is not None
        assert not memory_metadata.success
        assert len(memory_metadata.errors) > 0
