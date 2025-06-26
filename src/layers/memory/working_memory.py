# src/layers/memory/working_memory.py
from typing import Any, List, Dict, Optional
from dataclasses import dataclass
from collections import deque
import time

@dataclass
class MemoryItem:
    content: Any
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0
    importance: float = 0.5
    
    def access(self):
        """Обновление статистики доступа"""
        self.access_count += 1
        self.last_access = time.time()

class WorkingMemory:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.capacity = self.config.get('working_size', 7)  # 7±2 правило
        self.items: deque = deque(maxlen=self.capacity)
        self.item_map: Dict[str, MemoryItem] = {}
        
    def store(self, key: str, content: Any, importance: float = 0.5):
        """Сохранение элемента в рабочей памяти"""
        
        # Если элемент уже существует, обновляем его
        if key in self.item_map:
            self.item_map[key].content = content
            self.item_map[key].importance = importance
            self.item_map[key].access()
            return
            
        # Создаем новый элемент
        item = MemoryItem(
            content=content,
            timestamp=time.time(),
            importance=importance
        )
        
        # Если память заполнена, удаляем наименее важный элемент
        if len(self.items) >= self.capacity:
            self._evict_least_important()
            
        # Добавляем новый элемент
        self.items.append(key)
        self.item_map[key] = item
        
    def retrieve(self, key: str) -> Optional[Any]:
        """Извлечение элемента из рабочей памяти"""
        if key in self.item_map:
            item = self.item_map[key]
            item.access()
            return item.content
        return None
        
    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Поиск в рабочей памяти"""
        results = []
        
        for key, item in self.item_map.items():
            # Простой поиск по содержимому (строковое представление)
            content_str = str(item.content).lower()
            if query.lower() in content_str or query.lower() in key.lower():
                relevance = self._calculate_relevance(query, content_str, key)
                results.append({
                    'key': key,
                    'content': item.content,
                    'relevance': relevance,
                    'importance': item.importance,
                    'age': time.time() - item.timestamp
                })
                
        # Сортируем по релевантности
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:max_results]
        
    def get_current_context(self) -> List[Dict[str, Any]]:
        """Получение текущего контекста (всех элементов в рабочей памяти)"""
        context = []
        
        for key in self.items:
            if key in self.item_map:
                item = self.item_map[key]
                context.append({
                    'key': key,
                    'content': item.content,
                    'importance': item.importance,
                    'recency': time.time() - item.timestamp
                })
                
        return context
        
    def _evict_least_important(self):
        """Удаление наименее важного элемента"""
        if not self.items:
            return
            
        # Находим элемент с наименьшей важностью и наибольшим возрастом
        least_important_key = None
        min_score = float('inf')
        
        for key in self.items:
            if key in self.item_map:
                item = self.item_map[key]
                age = time.time() - item.timestamp
                # Комбинируем важность и возраст (старые менее важные элементы удаляются первыми)
                score = item.importance - (age / 3600.0)  # Возраст в часах снижает важность
                
                if score < min_score:
                    min_score = score
                    least_important_key = key
                    
        # Удаляем наименее важный элемент
        if least_important_key:
            self.items.remove(least_important_key)
            del self.item_map[least_important_key]
            
    def _calculate_relevance(self, query: str, content: str, key: str) -> float:
        """Расчет релевантности для поиска"""
        query_lower = query.lower()
        
        # Точное совпадение в ключе
        if query_lower == key.lower():
            return 1.0
            
        # Частичное совпадение в ключе
        if query_lower in key.lower():
            return 0.8
            
        # Совпадение в содержимом
        if query_lower in content:
            # Чем больше совпадений, тем выше релевантность
            matches = content.count(query_lower)
            relevance = min(matches * 0.2, 0.7)
            return relevance
            
        return 0.0
        
    def clear(self):
        """Очистка рабочей памяти"""
        self.items.clear()
        self.item_map.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики рабочей памяти"""
        if not self.items:
            return {
                'size': 0,
                'capacity': self.capacity,
                'utilization': 0.0,
                'avg_importance': 0.0,
                'avg_age': 0.0
            }
            
        current_time = time.time()
        ages = [current_time - self.item_map[key].timestamp for key in self.items if key in self.item_map]
        importances = [self.item_map[key].importance for key in self.items if key in self.item_map]
        
        return {
            'size': len(self.items),
            'capacity': self.capacity,
            'utilization': len(self.items) / self.capacity,
            'avg_importance': sum(importances) / len(importances) if importances else 0.0,
            'avg_age': sum(ages) / len(ages) if ages else 0.0
        }