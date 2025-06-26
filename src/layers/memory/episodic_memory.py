# src/layers/memory/episodic_memory.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time
import json
import sqlite3
import threading

@dataclass
class Episode:
    id: str
    content: Dict[str, Any]
    timestamp: float
    context: Dict[str, Any]
    emotional_valence: float
    importance: float
    tags: List[str]
    access_count: int = 0
    last_access: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сериализации"""
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp,
            'context': self.context,
            'emotional_valence': self.emotional_valence,
            'importance': self.importance,
            'tags': self.tags,
            'access_count': self.access_count,
            'last_access': self.last_access
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Episode':
        """Создание из словаря"""
        return cls(**data)

class EpisodicMemory:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_episodes = self.config.get('episodic_limit', 1000)
        self.db_path = self.config.get('db_path', 'data/episodic_memory.db')
        self.forgetting_rate = self.config.get('forgetting_rate', 0.01)
        
        self._lock = threading.Lock()
        self._init_database()
        
    def _init_database(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    timestamp REAL,
                    context TEXT,
                    emotional_valence REAL,
                    importance REAL,
                    tags TEXT,
                    access_count INTEGER,
                    last_access REAL
                )
            ''')
            
            # Создаем индексы для быстрого поиска
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON episodes(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_importance ON episodes(importance)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_emotional_valence ON episodes(emotional_valence)')
            
    def store_episode(self, episode_id: str, content: Dict[str, Any], 
                     context: Dict[str, Any], emotional_valence: float = 0.0,
                     importance: float = 0.5, tags: List[str] = None):
        """Сохранение эпизода"""
        
        if tags is None:
            tags = []
            
        episode = Episode(
            id=episode_id,
            content=content,
            timestamp=time.time(),
            context=context,
            emotional_valence=emotional_valence,
            importance=importance,
            tags=tags
        )
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO episodes 
                    (id, content, timestamp, context, emotional_valence, 
                     importance, tags, access_count, last_access)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    episode.id,
                    json.dumps(episode.content),
                    episode.timestamp,
                    json.dumps(episode.context),
                    episode.emotional_valence,
                    episode.importance,
                    json.dumps(episode.tags),
                    episode.access_count,
                    episode.last_access
                ))
                
        # Проверяем, не превышен ли лимит
        self._cleanup_if_needed()
        
    def retrieve_episode(self, episode_id: str) -> Optional[Episode]:
        """Извлечение конкретного эпизода"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT * FROM episodes WHERE id = ?', (episode_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    episode = self._row_to_episode(row)
                    # Обновляем статистику доступа
                    self._update_access_stats(episode_id)
                    return episode
                    
        return None
        
    def search_episodes(self, query: str = None, tags: List[str] = None,
                       emotional_range: tuple = None, importance_threshold: float = None,
                       time_range: tuple = None, max_results: int = 10) -> List[Episode]:
        """Поиск эпизодов по различным критериям"""
        
        conditions = []
        params = []
        
        # Поиск по содержимому
        if query:
            conditions.append("(content LIKE ? OR context LIKE ?)")
            params.extend([f'%{query}%', f'%{query}%'])
            
        # Поиск по тегам
        if tags:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            conditions.append(f"({' OR '.join(tag_conditions)})")
            
        # Фильтр по эмоциональной валентности
        if emotional_range:
            conditions.append("emotional_valence BETWEEN ? AND ?")
            params.extend(emotional_range)
            
        # Фильтр по важности
        if importance_threshold:
            conditions.append("importance >= ?")
            params.append(importance_threshold)
            
        # Фильтр по времени
        if time_range:
            conditions.append("timestamp BETWEEN ? AND ?")
            params.extend(time_range)
            
        # Формируем запрос
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
            
        sql = f'''
            SELECT * FROM episodes 
            {where_clause}
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        '''
        params.append(max_results)
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                
                episodes = [self._row_to_episode(row) for row in rows]
                
                # Обновляем статистику доступа для найденных эпизодов
                for episode in episodes:
                    self._update_access_stats(episode.id)
                    
                return episodes
                
    def get_recent_episodes(self, count: int = 5) -> List[Episode]:
        """Получение недавних эпизодов"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM episodes 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (count,))
                
                rows = cursor.fetchall()
                return [self._row_to_episode(row) for row in rows]
                
    def get_similar_episodes(self, reference_episode: Episode, 
                           similarity_threshold: float = 0.5,
                           max_results: int = 5) -> List[Episode]:
        """Поиск похожих эпизодов"""
        # Упрощенная реализация на основе тегов и эмоциональной валентности
        
        similar_episodes = []
        
        # Поиск по тегам
        if reference_episode.tags:
            episodes_with_tags = self.search_episodes(
                tags=reference_episode.tags,
                max_results=max_results * 2
            )
            
            for episode in episodes_with_tags:
                if episode.id != reference_episode.id:
                    similarity = self._calculate_similarity(reference_episode, episode)
                    if similarity >= similarity_threshold:
                        similar_episodes.append(episode)
                        
        # Поиск по эмоциональной близости
        emotional_range = (
            reference_episode.emotional_valence - 0.3,
            reference_episode.emotional_valence + 0.3
        )
        
        episodes_emotional = self.search_episodes(
            emotional_range=emotional_range,
            max_results=max_results * 2
        )
        
        for episode in episodes_emotional:
            if (episode.id != reference_episode.id and 
                episode not in similar_episodes):
                similarity = self._calculate_similarity(reference_episode, episode)
                if similarity >= similarity_threshold:
                    similar_episodes.append(episode)
                    
        # Сортируем по похожести и возвращаем топ результатов
        similar_episodes.sort(
            key=lambda ep: self._calculate_similarity(reference_episode, ep),
            reverse=True
        )
        
        return similar_episodes[:max_results]
        
    def _calculate_similarity(self, episode1: Episode, episode2: Episode) -> float:
        """Расчет похожести между эпизодами"""
        similarity = 0.0
        
        # Похожесть по тегам
        if episode1.tags and episode2.tags:
            common_tags = set(episode1.tags) & set(episode2.tags)
            all_tags = set(episode1.tags) | set(episode2.tags)
            tag_similarity = len(common_tags) / len(all_tags) if all_tags else 0.0
            similarity += tag_similarity * 0.4
            
        # Похожесть по эмоциональной валентности
        emotional_diff = abs(episode1.emotional_valence - episode2.emotional_valence)
        emotional_similarity = max(0.0, 1.0 - emotional_diff)
        similarity += emotional_similarity * 0.3
        
        # Похожесть по важности
        importance_diff = abs(episode1.importance - episode2.importance)
        importance_similarity = max(0.0, 1.0 - importance_diff)
        similarity += importance_similarity * 0.2
        
        # Временная близость (недавние эпизоды более похожи)
        time_diff = abs(episode1.timestamp - episode2.timestamp)
        max_time_diff = 30 * 24 * 3600  # 30 дней в секундах
        time_similarity = max(0.0, 1.0 - (time_diff / max_time_diff))
        similarity += time_similarity * 0.1
        
        return similarity
        
    def _row_to_episode(self, row) -> Episode:
        """Преобразование строки БД в объект Episode"""
        return Episode(
            id=row[0],
            content=json.loads(row[1]),
            timestamp=row[2],
            context=json.loads(row[3]),
            emotional_valence=row[4],
            importance=row[5],
            tags=json.loads(row[6]),
            access_count=row[7],
            last_access=row[8]
        )
        
    def _update_access_stats(self, episode_id: str):
        """Обновление статистики доступа"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE episodes 
                SET access_count = access_count + 1, last_access = ?
                WHERE id = ?
            ''', (time.time(), episode_id))
            
    def _cleanup_if_needed(self):
        """Очистка памяти при превышении лимита"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM episodes')
            count = cursor.fetchone()[0]
            
            if count > self.max_episodes:
                # Удаляем наименее важные и старые эпизоды
                episodes_to_remove = count - self.max_episodes + 100  # Удаляем с запасом
                
                conn.execute('''
                    DELETE FROM episodes 
                    WHERE id IN (
                        SELECT id FROM episodes 
                        ORDER BY importance ASC, timestamp ASC 
                        LIMIT ?
                    )
                ''', (episodes_to_remove,))
                
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики эпизодической памяти"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total_episodes,
                        AVG(importance) as avg_importance,
                        AVG(emotional_valence) as avg_emotional_valence,
                        MIN(timestamp) as oldest_episode,
                        MAX(timestamp) as newest_episode
                    FROM episodes
                ''')
                
                row = cursor.fetchone()
                
                return {
                    'total_episodes': row[0],
                    'avg_importance': row[1] or 0.0,
                    'avg_emotional_valence': row[2] or 0.0,
                    'oldest_episode': row[3] or 0.0,
                    'newest_episode': row[4] or 0.0,
                    'max_episodes': self.max_episodes,
                    'utilization': (row[0] / self.max_episodes) if self.max_episodes > 0 else 0.0
                }