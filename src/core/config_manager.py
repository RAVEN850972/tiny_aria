# src/core/config_manager.py
import json
import os
from typing import Dict, Any
import logging

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, environment: str = "development"):
        """Загрузка конфигурации для окружения"""
        # Загружаем базовую конфигурацию
        default_path = os.path.join(self.config_dir, "default.json")
        if os.path.exists(default_path):
            with open(default_path, 'r') as f:
                self.config = json.load(f)
                
        # Загружаем конфигурацию для конкретного окружения
        env_path = os.path.join(self.config_dir, f"{environment}.json")
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_config = json.load(f)
                self._merge_configs(self.config, env_config)
                
        self.logger.info(f"Configuration loaded for environment: {environment}")
        
    def _merge_configs(self, base: Dict, override: Dict):
        """Слияние конфигураций"""
        for key, value in override.items():
            if isinstance(value, dict) and key in base:
                self._merge_configs(base[key], value)
            else:
                base[key] = value
                
    def get(self, key: str, default=None):
        """Получение значения конфигурации"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value

