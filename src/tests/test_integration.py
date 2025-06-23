# src/tests/test_integration.py
import pytest
from src.tiny_aria import TinyARIA
import tempfile
import json
import os

class TestTinyARIAIntegration:
    def test_initialization(self):
        """Тест инициализации TinyARIA"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем минимальную конфигурацию
            config = {
                "perception": {"enabled": True},
                "memory": {"working_size": 7},
                "reasoning": {"max_steps": 10},
                "metacognition": {"confidence_threshold": 0.7},
                "ethics": {"harm_threshold": 0.1}
            }
            
            with open(os.path.join(temp_dir, "default.json"), 'w') as f:
                json.dump(config, f)
                
            aria = TinyARIA(temp_dir)
            assert aria.initialize() == True
            
    def test_basic_processing(self):
        """Тест базовой обработки ввода"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"test": True}
            
            with open(os.path.join(temp_dir, "default.json"), 'w') as f:
                json.dump(config, f)
                
            aria = TinyARIA(temp_dir)
            aria.initialize()
            
            response = aria.process_input("Hello, TinyARIA!")
            assert isinstance(response, str)
            assert len(response) > 0