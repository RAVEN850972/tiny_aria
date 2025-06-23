# src/tests/test_memory_layer.py
import pytest
import tempfile
import os
from src.layers.memory.working_memory import WorkingMemory
from src.layers.memory.episodic_memory import EpisodicMemory
from src.layers.memory.associations import AssociationNetwork
from src.layers.memory.memory_layer import MemoryLayer

class TestWorkingMemory:
    def test_store_and_retrieve(self):
        """Тест сохранения и извлечения из рабочей памяти"""
        wm = WorkingMemory({'working_size': 3})
        
        wm.store('test_key', 'test_content', importance=0.8)
        retrieved = wm.retrieve('test_key')
        
        assert retrieved == 'test_content'
        
    def test_capacity_limit(self):
        """Тест ограничения емкости"""
        wm = WorkingMemory({'working_size': 2})
        
        wm.store('key1', 'content1', importance=0.5)
        wm.store('key2', 'content2', importance=0.7)
        wm.store('key3', 'content3', importance=0.9)  # Должен вытеснить key1
        
        assert wm.retrieve('key1') is None  # Вытеснен
        assert wm.retrieve('key2') == 'content2'
        assert wm.retrieve('key3') == 'content3'
        
    def test_search(self):
        """Тест поиска в рабочей памяти"""
        wm = WorkingMemory()
        
        wm.store('greeting', 'Hello world', importance=0.8)
        wm.store('question', 'How are you?', importance=0.6)
        
        results = wm.search('hello')
        assert len(results) == 1
        assert results[0]['key'] == 'greeting'

class TestEpisodicMemory:
    def test_store_and_retrieve_episode(self):
        """Тест сохранения и извлечения эпизода"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, 'test_episodes.db')
            em = EpisodicMemory({'db_path': db_path})
            
            content = {'user_input': 'Hello', 'response': 'Hi there'}
            context = {'session_id': 'test_session'}
            
            em.store_episode(
                episode_id='test_episode',
                content=content,
                context=context,
                emotional_valence=0.5,
                importance=0.8,
                tags=['greeting', 'test']
            )
            
            episode = em.retrieve_episode('test_episode')
            
            assert episode is not None
            assert episode.content == content
            assert episode.importance == 0.8
            assert 'greeting' in episode.tags
            
    def test_search_episodes(self):
        """Тест поиска эпизодов"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, 'test_episodes.db')
            em = EpisodicMemory({'db_path': db_path})
            
            # Сохраняем несколько эпизодов
            em.store_episode('ep1', {'text': 'hello world'}, {}, 0.0, 0.8, ['greeting'])
            em.store_episode('ep2', {'text': 'goodbye world'}, {}, 0.0, 0.6, ['farewell'])
            em.store_episode('ep3', {'text': 'hello again'}, {}, 0.0, 0.7, ['greeting'])
            
            # Поиск по содержимому
            results = em.search_episodes(query='hello')
            assert len(results) == 2
            
            # Поиск по тегам
            results = em.search_episodes(tags=['greeting'])
            assert len(results) == 2
            
            # Поиск по важности
            results = em.search_episodes(importance_threshold=0.75)
            assert len(results) == 1

class TestAssociationNetwork:
    def test_create_association(self):
        """Тест создания ассоциации"""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, 'test_associations.pkl')
            an = AssociationNetwork({'save_path': save_path})
            
            an.create_association('cat', 'animal', 0.8, 'is_a')
            
            associations = an.get_associations('cat')
            assert len(associations) == 1
            assert associations[0]['concept'] == 'animal'
            assert associations[0]['strength'] == 0.8
            
    def test_concept_activation(self):
        """Тест активации концептов"""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, 'test_associations.pkl')
            an = AssociationNetwork({'save_path': save_path})
            
            # Создаем сеть ассоциаций
            an.create_association('dog', 'animal', 0.9)
            an.create_association('cat', 'animal', 0.8)
            an.create_association('dog', 'pet', 0.7)
            
            # Активируем концепт
            activations = an.activate_concepts(['dog'])
            
            assert 'dog' in activations
            assert 'animal' in activations
            assert 'pet' in activations
            assert activations['dog'] == 1.0
            
    def test_find_path(self):
        """Тест поиска пути между концептами"""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, 'test_associations.pkl')
            an = AssociationNetwork({'save_path': save_path})
            
            # Создаем цепочку ассоциаций
            an.create_association('dog', 'animal', 0.9)
            an.create_association('animal', 'living_being', 0.8)
            an.create_association('living_being', 'entity', 0.7)
            
            path = an.find_path('dog', 'entity')
            
            assert path is not None
            assert path[0] == 'dog'
            assert path[-1] == 'entity'
            assert len(path) <= 5  # Максимальная длина + 1

class TestMemoryLayerIntegration:
    def test_memory_layer_processing(self):
        """Тест интеграции слоя памяти"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                'episodic_memory': {'db_path': os.path.join(temp_dir, 'episodes.db')},
                'associations': {'save_path': os.path.join(temp_dir, 'associations.pkl')}
            }
            
            memory_layer = MemoryLayer(None, config)
            
            # Подготавливаем контекст с результатом восприятия
            context = {
                'user_input': 'Hello, how are you?',
                'processed_text': type('ProcessedText', (), {
                    'sentiment': 0.5,
                    'complexity': 0.3,
                    'keywords': ['hello', 'how']
                })(),
                'semantic_map': type('SemanticMap', (), {
                    'concepts': [
                        type('Concept', (), {
                            'name': 'greeting',
                            'category': 'social',
                            'confidence': 0.9
                        })()
                    ],
                    'relationships': [],
                    'abstraction_levels': {0: ['greeting'], 1: [], 2: []}
                })(),
                'context_analysis': type('ContextAnalysis', (), {
                    'primary_intent': 'greeting',
                    'emotional_tone': 'positive',
                    'complexity_level': 'low'
                })()
            }
            
            result = memory_layer.process(context)
            
            assert 'current_episode_id' in result
            assert 'working_memory_context' in result
            assert 'relevant_memories' in result
            assert 'memory_stats' in result
            assert result['processing_metadata']['layer'] == 'memory'