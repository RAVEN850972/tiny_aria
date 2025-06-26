# src/layers/base_layer.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLayer(ABC):
    """Базовый класс для всех когнитивных слоев"""
    
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
        
    def get_name(self) -> str:
        """Получение имени слоя"""
        return self.name
        
    def get_config(self) -> Dict[str, Any]:
        """Получение конфигурации слоя"""
        return self.config.copy()