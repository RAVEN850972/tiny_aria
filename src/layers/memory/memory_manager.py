# src/layers/memory/memory_manager.py
class MemoryManager:
    """Высокоуровневый менеджер для координации всех типов памяти"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.working_memory = WorkingMemory(config.get('working_memory', {}))
        self.episodic_memory = EpisodicMemory(config.get('episodic_memory', {}))
        self.associations = AssociationNetwork(config.get('associations', {}))
        
        # Счетчики для автоматической консолидации
        self.consolidation_counter = 0
        self.consolidation_threshold = config.get('consolidation_threshold', 100)
        
    def comprehensive_search(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Комплексный поиск по всем типам памяти"""
        
        results = {
            'working_memory': [],
            'episodic_memory': [],
            'associations': [],
            'consolidated_results': []
        }
        
        # Поиск в рабочей памяти
        wm_results = self.working_memory.search(query, max_results=5)
        results['working_memory'] = wm_results
        
        # Поиск в эпизодической памяти
        em_results = self.episodic_memory.search_episodes(query=query, max_results=5)
        results['episodic_memory'] = [ep.to_dict() for ep in em_results]
        
        # Поиск связанных концептов
        related_concepts = []
        if context and 'concepts' in context:
            for concept in context['concepts']:
                associations = self.associations.get_associations(concept, max_results=3)
                related_concepts.extend(associations)
                
        results['associations'] = related_concepts
        
        # Консолидация результатов
        consolidated = self._consolidate_search_results(results, query)
        results['consolidated_results'] = consolidated
        
        return results
        
    def _consolidate_search_results(self, results: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Консолидация результатов поиска из разных источников"""
        
        consolidated = []
        
        # Обрабатываем результаты из рабочей памяти
        for result in results['working_memory']:
            consolidated.append({
                'source': 'working_memory',
                'content': result['content'],
                'relevance': result['relevance'],
                'recency_bonus': 0.3,  # Бонус за актуальность
                'final_score': result['relevance'] + 0.3
            })
            
        # Обрабатываем результаты из эпизодической памяти
        for result in results['episodic_memory']:
            base_score = result['importance']
            recency_penalty = min((time.time() - result['timestamp']) / (30 * 24 * 3600), 0.5)
            
            consolidated.append({
                'source': 'episodic_memory',
                'content': result['content'],
                'relevance': base_score,
                'recency_penalty': recency_penalty,
                'final_score': base_score - recency_penalty
            })
            
        # Обрабатываем ассоциации
        for result in results['associations']:
            consolidated.append({
                'source': 'associations',
                'content': result,
                'relevance': result['strength'],
                'association_bonus': 0.2,
                'final_score': result['strength'] + 0.2
            })
            
        # Сортируем по финальному счету
        consolidated.sort(key=lambda x: x['final_score'], reverse=True)
        
        return consolidated[:10]  # Топ 10 результатов
        
    def trigger_consolidation(self):
        """Запуск процесса консолидации памяти"""
        
        self.consolidation_counter += 1
        
        if self.consolidation_counter >= self.consolidation_threshold:
            self._perform_memory_consolidation()
            self.consolidation_counter = 0
            
    def _perform_memory_consolidation(self):
        """Выполнение консолидации памяти"""
        
        # Получаем недавние эпизоды для анализа
        recent_episodes = self.episodic_memory.get_recent_episodes(count=50)
        
        # Анализируем паттерны в недавних эпизодах
        patterns = self._analyze_episode_patterns(recent_episodes)
        
        # Обновляем ассоциации на основе найденных паттернов
        for pattern in patterns:
            self._reinforce_pattern_associations(pattern)
            
        # Очистка слабых ассоциаций
        self.associations._cleanup_weak_associations()
        
        # Сохраняем состояние
        self.associations.save_associations()
        
    def _analyze_episode_patterns(self, episodes: List[Any]) -> List[Dict[str, Any]]:
        """Анализ паттернов в эпизодах"""
        
        patterns = []
        
        # Группируем эпизоды по тегам
        tag_groups = {}
        for episode in episodes:
            for tag in episode.tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(episode)
                
        # Ищем часто встречающиеся комбинации тегов
        for tag, tag_episodes in tag_groups.items():
            if len(tag_episodes) >= 3:  # Минимум 3 эпизода для паттерна
                patterns.append({
                    'type': 'tag_frequency',
                    'tag': tag,
                    'episodes': tag_episodes,
                    'strength': len(tag_episodes) / len(episodes)
                })
                
        return patterns
        
    def _reinforce_pattern_associations(self, pattern: Dict[str, Any]):
        """Усиление ассоциаций на основе паттерна"""
        
        if pattern['type'] == 'tag_frequency':
            tag = pattern['tag']
            episodes = pattern['episodes']
            
            # Создаем ассоциации между концептами из эпизодов с этим тегом
            concepts = []
            for episode in episodes:
                # Извлекаем концепты из содержимого эпизода
                if 'semantic_map' in episode.content:
                    for concept in episode.content['semantic_map'].get('concepts', []):
                        concepts.append(concept['name'])
                        
            # Создаем ассоциации между концептами
            for i, concept1 in enumerate(concepts):
                for concept2 in concepts[i+1:]:
                    self.associations.create_association(
                        concept1, concept2, 
                        strength=pattern['strength'] * 0.5,
                        association_type=f'pattern_{tag}'
                    )