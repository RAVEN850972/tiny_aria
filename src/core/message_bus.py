# src/core/message_bus.py
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
from datetime import datetime

class MessageType(Enum):
    SYSTEM = "system"
    COGNITIVE = "cognitive"
    USER_INPUT = "user_input"
    RESPONSE = "response"
    ERROR = "error"
    METRIC = "metric"

@dataclass
class Message:
    id: str
    type: MessageType
    source: str
    target: str
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 0

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[MessageType, List[Callable]] = {}
        self.message_queue: List[Message] = []
        self.logger = logging.getLogger(__name__)
        self.running = False
        
    def subscribe(self, message_type: MessageType, handler: Callable):
        """Подписка на тип сообщений"""
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        self.subscribers[message_type].append(handler)
        self.logger.info(f"Handler {handler.__name__} subscribed to {message_type}")
        
    def publish(self, message: Message):
        """Публикация сообщения"""
        self.message_queue.append(message)
        self.logger.debug(f"Message {message.id} published")
        
    def process_messages(self):
        """Обработка очереди сообщений"""
        # Сортировка по приоритету
        self.message_queue.sort(key=lambda x: x.priority, reverse=True)
        
        while self.message_queue:
            message = self.message_queue.pop(0)
            self._deliver_message(message)
            
    def _deliver_message(self, message: Message):
        """Доставка сообщения подписчикам"""
        if message.type in self.subscribers:
            for handler in self.subscribers[message.type]:
                try:
                    handler(message)
                except Exception as e:
                    self.logger.error(f"Error in handler {handler.__name__}: {e}")