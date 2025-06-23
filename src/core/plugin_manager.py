# src/core/plugin_manager.py
import importlib
import os
import json
from typing import Dict, Any, List
from abc import ABC, abstractmethod
import logging

class PluginInterface(ABC):
    """Базовый интерфейс для всех плагинов"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]):
        """Инициализация плагина"""
        pass
        
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Основная обработка данных"""
        pass
        
    @abstractmethod
    def shutdown(self):
        """Корректное завершение работы"""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Имя плагина"""
        pass

class PluginManager:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.plugin_configs: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
        
    def discover_plugins(self) -> List[str]:
        """Обнаружение доступных плагинов"""
        plugins = []
        if not os.path.exists(self.plugins_dir):
            return plugins
            
        for item in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, item)
            if os.path.isdir(plugin_path) and not item.startswith('__'):
                # Проверяем наличие __init__.py и plugin.json
                init_file = os.path.join(plugin_path, '__init__.py')
                config_file = os.path.join(plugin_path, 'plugin.json')
                
                if os.path.exists(init_file) and os.path.exists(config_file):
                    plugins.append(item)
                    
        return plugins
        
    def load_plugin(self, plugin_name: str) -> bool:
        """Загрузка конкретного плагина"""
        try:
            # Загружаем конфигурацию плагина
            config_path = os.path.join(self.plugins_dir, plugin_name, 'plugin.json')
            with open(config_path, 'r') as f:
                plugin_config = json.load(f)
                
            # Проверяем совместимость версий
            if not self._check_compatibility(plugin_config):
                self.logger.error(f"Plugin {plugin_name} is not compatible")
                return False
                
            # Импортируем модуль плагина
            module_name = f"plugins.{plugin_name}"
            module = importlib.import_module(module_name)
            
            # Получаем класс плагина
            plugin_class_name = plugin_config.get('class_name', 'Plugin')
            plugin_class = getattr(module, plugin_class_name)
            
            # Создаем экземпляр плагина
            plugin_instance = plugin_class()
            
            # Инициализируем плагин
            plugin_instance.initialize(plugin_config.get('config', {}))
            
            # Сохраняем плагин
            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_configs[plugin_name] = plugin_config
            
            self.logger.info(f"Plugin {plugin_name} loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
            
    def _check_compatibility(self, plugin_config: Dict) -> bool:
        """Проверка совместимости плагина"""
        required_version = plugin_config.get('required_version', '1.0.0')
        # Простая проверка версии (в реальности может быть сложнее)
        return True  # Упрощенная реализация
        
    def get_plugin(self, plugin_name: str) -> PluginInterface:
        """Получение загруженного плагина"""
        return self.loaded_plugins.get(plugin_name)
        
    def shutdown_all(self):
        """Корректное завершение всех плагинов"""
        for plugin_name, plugin in self.loaded_plugins.items():
            try:
                plugin.shutdown()
                self.logger.info(f"Plugin {plugin_name} shut down")
            except Exception as e:
                self.logger.error(f"Error shutting down plugin {plugin_name}: {e}")