# src/core/lifecycle_manager.py
from enum import Enum
import logging
from typing import List, Callable

class SystemState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class LifecycleManager:
    def __init__(self):
        self.state = SystemState.STOPPED
        self.initialization_hooks: List[Callable] = []
        self.shutdown_hooks: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        
    def add_initialization_hook(self, hook: Callable):
        """Добавление хука инициализации"""
        self.initialization_hooks.append(hook)
        
    def add_shutdown_hook(self, hook: Callable):
        """Добавление хука завершения"""
        self.shutdown_hooks.append(hook)
        
    def initialize(self):
        """Инициализация системы"""
        self.state = SystemState.INITIALIZING
        self.logger.info("System initialization started")
        
        try:
            for hook in self.initialization_hooks:
                if callable(hook):
                    hook()
                else:
                    self.logger.warning(f"Skipping non-callable hook: {hook}")
                
            self.state = SystemState.RUNNING
            self.logger.info("System initialization completed")
            return True
            
        except Exception as e:
            self.state = SystemState.ERROR
            self.logger.error(f"System initialization failed: {e}")
            return False
            
    def shutdown(self):
        """Завершение работы системы"""
        self.state = SystemState.STOPPING
        self.logger.info("System shutdown started")
        
        for hook in reversed(self.shutdown_hooks):  # Обратный порядок
            try:
                if callable(hook):
                    hook()
            except Exception as e:
                self.logger.error(f"Error in shutdown hook: {e}")
                
        self.state = SystemState.STOPPED
        self.logger.info("System shutdown completed")