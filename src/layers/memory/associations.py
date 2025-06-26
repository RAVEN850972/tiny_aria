# src/layers/memory/associations.py
import networkx as nx
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import time
import pickle
import os

class AssociationNetwork:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.graph = nx.Graph()
        self.association_threshold = self.config.get('association_threshold', 0.5)
        self.max_associations = self.config.get('max_associations', 1000)
        self.decay_rate = self.config.get('decay_rate', 0.01)
        
        self.save_path = self.config.get('save_path', 'data/associations.pkl')
        
        # Загружаем существующие ассоциации
        self._load_associations()
        
    def create_association(self, concept1: str, concept2: str, 
                          strength: float, association_type: str = 'general'):
        """Создание ассоциации между концептами"""
        
        # Добавляем узлы если их нет
        if not self.graph.has_node(concept1):
            self.graph.add_node(concept1, 
                              creation_time=time.time(),
                              activation_count=0,
                              last_activation=time.time())
            
        if not self.graph.has_node(concept2):
            self.graph.add_node(concept2,
                              creation_time=time.time(), 
                              activation_count=0,
                              last_activation=time.time())
            
        # Создаем или обновляем ребро
        if self.graph.has_edge(concept1, concept2):
            # Обновляем существующую ассоциацию
            current_strength = self.graph[concept1][concept2]['strength']
            # Комбинируем силы (среднее взвешенное)
            new_strength = (current_strength + strength) / 2.0
            self.graph[concept1][concept2]['strength'] = new_strength
            self.graph[concept1][concept2]['last_reinforcement'] = time.time()
            self.graph[concept1][concept2]['reinforcement_count'] += 1
        else:
            # Создаем новую ассоциацию
            self.graph.add_edge(concept1, concept2,
                              strength=strength,
                              type=association_type,
                              creation_time=time.time(),
                              last_reinforcement=time.time(),
                              reinforcement_count=1)
            
        # Проверяем лимиты
        self._cleanup_weak_associations()
        
    def get_associations(self, concept: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Получение ассоциаций для концепта"""
        if not self.graph.has_node(concept):
            return []
            
        # Обновляем статистику активации
        self._activate_concept(concept)
        
        associations = []
        
        for neighbor in self.graph.neighbors(concept):
            edge_data = self.graph[concept][neighbor]
            
            # Применяем временное затухание
            current_strength = self._apply_decay(edge_data)
            
            if current_strength >= self.association_threshold:
                associations.append({
                    'concept': neighbor,
                    'strength': current_strength,
                    'type': edge_data.get('type', 'general'),
                    'age': time.time() - edge_data['creation_time'],
                    'reinforcements': edge_data['reinforcement_count']
                })
                
        # Сортируем по силе ассоциации
        associations.sort(key=lambda x: x['strength'], reverse=True)
        
        return associations[:max_results]
        
    def activate_concepts(self, concepts: List[str]) -> Dict[str, float]:
        """Активация концептов и распространение по сети"""
        
        activation_levels = {}
        
        # Инициализируем начальную активацию
        for concept in concepts:
            if self.graph.has_node(concept):
                activation_levels[concept] = 1.0
                self._activate_concept(concept)
                
        # Распространяем активацию по сети (один шаг)
        secondary_activations = {}
        
        for concept in concepts:
            if concept in activation_levels:
                associations = self.get_associations(concept)
                
                for assoc in associations:
                    neighbor = assoc['concept']
                    # Активация затухает пропорционально силе связи
                    propagated_activation = activation_levels[concept] * assoc['strength']
                    
                    if neighbor in secondary_activations:
                        secondary_activations[neighbor] = max(
                            secondary_activations[neighbor], 
                            propagated_activation
                        )
                    else:
                        secondary_activations[neighbor] = propagated_activation
                        
        # Объединяем первичную и вторичную активацию
        all_activations = activation_levels.copy()
        for concept, activation in secondary_activations.items():
            if concept not in all_activations:
                all_activations[concept] = activation * 0.5  # Вторичная активация слабее
                
        return all_activations
        
    def find_path(self, start_concept: str, end_concept: str, max_length: int = 4) -> Optional[List[str]]:
        """Поиск пути между концептами"""
        
        if not (self.graph.has_node(start_concept) and self.graph.has_node(end_concept)):
            return None
            
        try:
            # Используем взвешенный кратчайший путь
            # Вес = 1 / strength (чем сильнее связь, тем меньше вес)
            weighted_graph = self.graph.copy()
            
            for u, v, data in weighted_graph.edges(data=True):
                current_strength = self._apply_decay(data)
                weight = 1.0 / max(current_strength, 0.01)  # Избегаем деления на ноль
                weighted_graph[u][v]['weight'] = weight
                
            path = nx.shortest_path(
                weighted_graph, 
                start_concept, 
                end_concept, 
                weight='weight'
            )
            
            if len(path) <= max_length + 1:  # +1 потому что path включает начальный и конечный узлы
                return path
            else:
                return None
                
        except nx.NetworkXNoPath:
            return None
            
    def get_concept_clusters(self, min_cluster_size: int = 3) -> List[List[str]]:
        """Поиск кластеров связанных концептов"""
        
        # Создаем граф только с сильными связями
        strong_graph = nx.Graph()
        
        for u, v, data in self.graph.edges(data=True):
            current_strength = self._apply_decay(data)
            if current_strength >= self.association_threshold * 1.5:  # Повышенный порог
                strong_graph.add_edge(u, v, strength=current_strength)
                
        # Ищем связанные компоненты
        clusters = []
        for component in nx.connected_components(strong_graph):
            if len(component) >= min_cluster_size:
                clusters.append(list(component))
                
        return clusters
        
    def _activate_concept(self, concept: str):
        """Обновление статистики активации концепта"""
        if self.graph.has_node(concept):
            self.graph.nodes[concept]['activation_count'] += 1
            self.graph.nodes[concept]['last_activation'] = time.time()
            
    def _apply_decay(self, edge_data: Dict[str, Any]) -> float:
        """Применение временного затухания к силе ассоциации"""
        base_strength = edge_data['strength']
        time_since_reinforcement = time.time() - edge_data['last_reinforcement']
        
        # Экспоненциальное затухание
        decay_factor = np.exp(-self.decay_rate * time_since_reinforcement / 3600)  # Час = единица времени
        
        return base_strength * decay_factor
        
    def _cleanup_weak_associations(self):
        """Удаление слабых ассоциаций для экономии памяти"""
        
        if self.graph.number_of_edges() <= self.max_associations:
            return
            
        # Собираем все ребра с их текущей силой
        edges_with_strength = []
        
        for u, v, data in self.graph.edges(data=True):
            current_strength = self._apply_decay(data)
            edges_with_strength.append((u, v, current_strength))
            
        # Сортируем по силе (слабые в начале)
        edges_with_strength.sort(key=lambda x: x[2])
        
        # Удаляем самые слабые ребра
        edges_to_remove = self.graph.number_of_edges() - self.max_associations + 100
        
        for i in range(min(edges_to_remove, len(edges_with_strength))):
            u, v, _ = edges_with_strength[i]
            self.graph.remove_edge(u, v)
            
        # Удаляем изолированные узлы
        isolated_nodes = list(nx.isolates(self.graph))
        self.graph.remove_nodes_from(isolated_nodes)
        
    def save_associations(self):
        """Сохранение сети ассоциаций"""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        
        with open(self.save_path, 'wb') as f:
            pickle.dump(self.graph, f)
            
    def _load_associations(self):
        """Загрузка сети ассоциаций"""
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'rb') as f:
                    self.graph = pickle.load(f)
            except Exception as e:
                print(f"Error loading associations: {e}")
                self.graph = nx.Graph()
                
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики сети ассоциаций"""
        
        if self.graph.number_of_nodes() == 0:
            return {
                'nodes': 0,
                'edges': 0,
                'avg_degree': 0.0,
                'clustering_coefficient': 0.0,
                'connected_components': 0
            }
            
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
            'clustering_coefficient': nx.average_clustering(self.graph),
            'connected_components': nx.number_connected_components(self.graph),
            'density': nx.density(self.graph)
        }