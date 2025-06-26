# src/tests/test_core.py
import pytest
import tempfile
import os
import json
from src.core.message_bus import MessageBus, Message, MessageType
from src.core.config_manager import ConfigManager
from src.core.plugin_manager import PluginManager
from datetime import datetime

class TestMessageBus:
    def test_subscribe_and_publish(self):
        """Тест подписки и публикации сообщений"""
        bus = MessageBus()
        received_messages = []
        
        def handler(message):
            received_messages.append(message)
            
        bus.subscribe(MessageType.SYSTEM, handler)
        
        test_message = Message(
            id="test_1",
            type=MessageType.SYSTEM,
            source="test",
            target="test",
            payload={"data": "test"},
            timestamp=datetime.now()
        )
        
        bus.publish(test_message)
        bus.process_messages()
        
        assert len(received_messages) == 1
        assert received_messages[0].id == "test_1"
        
    def test_message_priority(self):
        """Тест приоритета сообщений"""
        bus = MessageBus()
        processed_order = []
        
        def handler(message):
            processed_order.append(message.priority)
            
        bus.subscribe(MessageType.SYSTEM, handler)
        
        # Добавляем сообщения с разными приоритетами
        for priority in [1, 3, 2]:
            message = Message(
                id=f"test_{priority}",
                type=MessageType.SYSTEM,
                source="test",
                target="test",
                payload={},
                timestamp=datetime.now(),
                priority=priority
            )
            bus.publish(message)
            
        bus.process_messages()
        
        # Проверяем, что сообщения обработались в порядке приоритета
        assert processed_order == [3, 2, 1]

class TestConfigManager:
    def test_load_config(self):
        """Тест загрузки конфигурации"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем тестовые конфигурационные файлы
            default_config = {"setting1": "default", "setting2": 42}
            dev_config = {"setting1": "development", "setting3": True}
            
            with open(os.path.join(temp_dir, "default.json"), 'w') as f:
                json.dump(default_config, f)
                
            with open(os.path.join(temp_dir, "development.json"), 'w') as f:
                json.dump(dev_config, f)
                
            # Тестируем загрузку
            config_manager = ConfigManager(temp_dir)
            config_manager.load_config("development")
            
            assert config_manager.get("setting1") == "development"
            assert config_manager.get("setting2") == 42
            assert config_manager.get("setting3") == True
            
    def test_nested_config_access(self):
        """Тест доступа к вложенным конфигурациям"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {
                        "username": "test",
                        "password": "secret"
                    }
                }
            }
            
            with open(os.path.join(temp_dir, "default.json"), 'w') as f:
                json.dump(config, f)
                
            config_manager = ConfigManager(temp_dir)
            config_manager.load_config()
            
            assert config_manager.get("database.host") == "localhost"
            assert config_manager.get("database.credentials.username") == "test"
            assert config_manager.get("nonexistent", "default_value") == "default_value"