# src/layers/memory/memory_layer.py
from typing import Dict, Any, List
import logging
import hashlib
import time
from ..base_layer import BaseLayer
from .working_memory import WorkingMemory
from .episodic_memory import EpisodicMemory
from .associations import AssociationNetwork

class MemoryLayer(BaseLayer):
    def __init__(self, message_bus, config: Dict[str, Any]):
        super().__init__("memory", message_bus, config)
        
        self.working_memory = WorkingMemory(config.get('working_memory', {}))
        self.episodic_memory = EpisodicMemory(config.get('episodic_memory', {}))
        self.associations = AssociationNetwork(config.get('associations', {}))
        
        self.logger = logging.getLogger(__name__)
        
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Основная обработка в слое памяти"""
        try:
            # Извлекаем релевантную информацию из контекста
            user_input = context.get('user_input', '')
            perception_result = context.get('perception_result', {})
            
            # Сохраняем текущий ввод в рабочую память
            self._store_in_working_memory(user_input, perception_result)
            
            # Создаем эпизод
            episode_id = self._create_episode(user_input, perception_result, context)
            
            # Обновляем ассоциации
            self._update_associations(perception_result)
            
            # Поиск релевантных воспоминаний
            relevant_memories = self._retrieve_relevant_memories(user_input, perception_result)
            
            # Активация концептов
            activated_concepts = self._activate_concepts(perception_result)
            
            result = {
                'current_episode_id': episode_id,
                'working_memory_context': self.working_memory.get_current_context(),
                'relevant_memories': relevant_memories,
                'activated_concepts': activated_concepts,
                'memory_stats': self._get_memory_stats(),
                'processing_metadata': {
                    'layer': 'memory',
                    'episode_created': episode_id is not None,
                    'associations_updated': True,
                    'concepts_activated': len(activated_concepts)
                }
            }
            
            self.logger.info(f"Memory processing completed. Episode: {episode_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in memory layer: {e}")
            return {
                'error': str(e),
                'memory_stats': self._get_memory_stats()
            }
            
    def _store_in_working_memory(self, user_input: str, perception_result: Dict[str, Any]):
        """Сохранение в рабочую память"""
        
        # Сохраняем пользовательский ввод
        input_key = f"user_input_{int(time.time())}"
        self.working_memory.store(input_key, user_input, importance=0.8)
        
        # Сохраняем ключевые концепты из восприятия
        if 'semantic_map' in perception_result:
            semantic_map = perception_result['semantic_map']
            
            for concept in semantic_map.concepts[:5]:  # Топ 5 концептов
                concept_key = f"concept_{concept.name}"
                self.working_memory.store(
                    concept_key, 
                    concept, 
                    importance=concept.confidence
                )
                
    def _create_episode(self, user_input: str, perception_result: Dict[str, Any], 
                       context: Dict[str, Any]) -> str:
        """Создание эпизода в эпизодической памяти"""
        
        # Генерируем уникальный ID эпизода
        episode_content = f"{user_input}_{time.time()}"
        episode_id = hashlib.md5(episode_content.encode()).hexdigest()
        
        # Подготавливаем содержимое эпизода
        episode_content = {
            'user_input': user_input,
            'perception_result': perception_result,
            'timestamp': time.time()
        }
        
        # Подготавливаем контекст эпизода
        episode_context = {
            'working_memory_state': self.working_memory.get_current_context(),
            'session_info': context.get('session_info', {}),
            'system_state': context.get('system_state', {})
        }
        
        # Определяем эмоциональную валентность
        emotional_valence = 0.0
        if 'processed_text' in perception_result:
            emotional_valence = perception_result['processed_text'].sentiment
            
        # Определяем важность эпизода
        importance = self._calculate_episode_importance(perception_result, context)
        
        # Генерируем теги
        tags = self._generate_episode_tags(perception_result)
        
        # Сохраняем эпизод
        self.episodic_memory.store_episode(
            episode_id=episode_id,
            content=episode_content,
            context=episode_context,
            emotional_valence=emotional_valence,
            importance=importance,
            tags=tags
        )
        
        return episode_id
        
    def _calculate_episode_importance(self, perception_result: Dict[str, Any], 
                                    context: Dict[str, Any]) -> float:
        """Расчет важности эпизода"""
        importance = 0.5  # Базовая важность
        
        # Увеличиваем важность для сложных входов
        if 'processed_text' in perception_result:
            complexity = perception_result['processed_text'].complexity
            importance += complexity * 0.3
            
        # Увеличиваем важность для эмоционально окрашенных входов
        if 'processed_text' in perception_result:
            sentiment_abs = abs(perception_result['processed_text'].sentiment)
            importance += sentiment_abs * 0.2
            
        # Увеличиваем важность для входов с много концептов
        if 'semantic_map' in perception_result:
            concept_count = len(perception_result['semantic_map'].concepts)
            importance += min(concept_count / 10.0, 0.3)
            
        # Увеличиваем важность для вопросов
        if 'context_analysis' in perception_result:
            intent = perception_result['context_analysis'].primary_intent
            if intent == 'question':
                importance += 0.2
                
        return min(importance, 1.0)
        
    def _generate_episode_tags(self, perception_result: Dict[str, Any]) -> List[str]:
        """Генерация тегов для эпизода"""
        tags = []
        
        # Теги из контекстного анализа
        if 'context_analysis' in perception_result:
            context_analysis = perception_result['context_analysis']
            tags.append(f"intent_{context_analysis.primary_intent}")
            tags.append(f"emotion_{context_analysis.emotional_tone}")
            tags.append(f"complexity_{context_analysis.complexity_level}")
            
        # Теги из семантической карты
        if 'semantic_map' in perception_result:
            semantic_map = perception_result['semantic_map']
            
            # Добавляем категории концептов как теги
            categories = set()
            for concept in semantic_map.concepts:
                categories.add(concept.category)
                
            for category in categories:
                tags.append(f"category_{category}")
                
            # Добавляем уровни абстракции
            for level, concepts in semantic_map.abstraction_levels.items():
                if concepts:
                    tags.append(f"abstraction_level_{level}")
                    
        # Теги из обработанного текста
        if 'processed_text' in perception_result:
            processed_text = perception_result['processed_text']
            tags.append(f"language_{processed_text.language}")
            
            # Добавляем ключевые слова как теги
            for keyword in processed_text.keywords[:5]:  # Максимум 5 ключевых слов
                tags.append(f"keyword_{keyword}")
                
        return tags
        
    def _update_associations(self, perception_result: Dict[str, Any]):
        """Обновление ассоциативной сети"""
        
        if 'semantic_map' not in perception_result:
            return
            
        semantic_map = perception_result['semantic_map']
        
        # Создаем ассоциации между концептами
        for relationship in semantic_map.relationships:
            self.associations.create_association(
                concept1=relationship.source,
                concept2=relationship.target,
                strength=relationship.strength,
                association_type=relationship.relation_type
            )
            
        # Создаем ассоциации между концептами одного уровня абстракции
        for level, concepts in semantic_map.abstraction_levels.items():
            for i, concept1 in enumerate(concepts):
                for concept2 in concepts[i+1:]:
                    # Слабая ассоциация между концептами одного уровня
                    self.associations.create_association(
                        concept1=concept1,
                        concept2=concept2,
                        strength=0.3,
                        association_type=f"same_level_{level}"
                    )
                    
    def _retrieve_relevant_memories(self, user_input: str, 
                                   perception_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Поиск релевантных воспоминаний"""
        
        relevant_memories = []
        
        # Поиск в рабочей памяти
        working_memory_results = self.working_memory.search(user_input, max_results=3)
        for result in working_memory_results:
            relevant_memories.append({
                'source': 'working_memory',
                'type': 'recent_context',
                'content': result,
                'relevance': result['relevance']
            })
            
        # Поиск в эпизодической памяти по ключевым словам
        if 'processed_text' in perception_result:
            keywords = perception_result['processed_text'].keywords
            
            for keyword in keywords[:3]:  # Топ 3 ключевых слова
                episodes = self.episodic_memory.search_episodes(
                    query=keyword,
                    max_results=2
                )
                
                for episode in episodes:
                    relevant_memories.append({
                        'source': 'episodic_memory',
                        'type': 'keyword_match',
                        'content': episode.to_dict(),
                        'relevance': episode.importance,
                        'keyword': keyword
                    })
                    
        # Поиск похожих эпизодов по эмоциональной валентности
        if 'processed_text' in perception_result:
            sentiment = perception_result['processed_text'].sentiment
            
            if abs(sentiment) > 0.3:  # Только для эмоционально окрашенных входов
                emotional_episodes = self.episodic_memory.search_episodes(
                    emotional_range=(sentiment - 0.2, sentiment + 0.2),
                    max_results=2
                )
                
                for episode in emotional_episodes:
                    relevant_memories.append({
                        'source': 'episodic_memory',
                        'type': 'emotional_similarity',
                        'content': episode.to_dict(),
                        'relevance': episode.importance,
                        'emotional_distance': abs(sentiment - episode.emotional_valence)
                    })
                    
        # Сортируем по релевантности
        relevant_memories.sort(key=lambda x: x['relevance'], reverse=True)
        
        return relevant_memories[:10]  # Максимум 10 релевантных воспоминаний
        
    def _activate_concepts(self, perception_result: Dict[str, Any]) -> Dict[str, float]:
        """Активация концептов в ассоциативной сети"""
        
        if 'semantic_map' not in perception_result:
            return {}
            
        semantic_map = perception_result['semantic_map']
        
        # Собираем концепты для активации
        concepts_to_activate = []
        
        for concept in semantic_map.concepts:
            if concept.confidence > 0.5:  # Активируем только уверенные концепты
                concepts_to_activate.append(concept.name)
                
        # Активируем концепты в сети
        if concepts_to_activate:
            activated_concepts = self.associations.activate_concepts(concepts_to_activate)
            return activated_concepts
        else:
            return {}
            
    def _get_memory_stats(self) -> Dict[str, Any]:
        """Получение статистики памяти"""
        return {
            'working_memory': self.working_memory.get_stats(),
            'episodic_memory': self.episodic_memory.get_stats(),
            'associations': self.associations.get_stats()
        }
        
    def shutdown(self):
        """Корректное завершение работы слоя памяти"""
        try:
            # Сохраняем ассоциации
            self.associations.save_associations()
            self.logger.info("Memory layer shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during memory layer shutdown: {e}")