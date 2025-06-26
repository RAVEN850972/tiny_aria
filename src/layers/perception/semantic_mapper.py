# src/layers/perception/semantic_mapper.py
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from .text_processor import ProcessedText
from .context_analyzer import ContextAnalysis

@dataclass
class Concept:
    name: str
    category: str
    confidence: float
    attributes: Dict[str, Any]

@dataclass
class Relationship:
    source: str
    target: str
    relation_type: str
    strength: float

@dataclass
class SemanticMap:
    concepts: List[Concept]
    relationships: List[Relationship]
    abstraction_levels: Dict[int, List[str]]
    semantic_vector: np.ndarray
    complexity_score: float

class SemanticMapper:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.vector_dimension = self.config.get('vector_dimension', 100)
        
        # Простые семантические категории
        self.semantic_categories = {
            'entity': ['PERSON', 'ORG', 'GPE', 'PRODUCT'],
            'action': ['VERB'],
            'quality': ['ADJ'],
            'time': ['DATE', 'TIME'],
            'quantity': ['MONEY', 'PERCENT', 'QUANTITY']
        }
        
    def create_map(self, processed_text: ProcessedText, context_analysis: ContextAnalysis) -> SemanticMap:
        """Создание семантической карты"""
        
        # Извлечение концептов
        concepts = self._extract_concepts(processed_text, context_analysis)
        
        # Определение отношений
        relationships = self._extract_relationships(concepts, processed_text)
        
        # Построение иерархии абстракций
        abstraction_levels = self._build_abstraction_hierarchy(concepts)
        
        # Создание семантического вектора
        semantic_vector = self._create_semantic_vector(concepts, relationships)
        
        # Расчет сложности
        complexity_score = self._calculate_map_complexity(concepts, relationships)
        
        return SemanticMap(
            concepts=concepts,
            relationships=relationships,
            abstraction_levels=abstraction_levels,
            semantic_vector=semantic_vector,
            complexity_score=complexity_score
        )
        
    def _extract_concepts(self, processed_text: ProcessedText, context_analysis: ContextAnalysis) -> List[Concept]:
        """Извлечение концептов из текста"""
        concepts = []
        
        # Концепты из именованных сущностей
        for entity in processed_text.entities:
            category = self._map_entity_to_category(entity['label'])
            concept = Concept(
                name=entity['text'],
                category=category,
                confidence=0.8,  # Высокая уверенность для именованных сущностей
                attributes={
                    'entity_type': entity['label'],
                    'position': (entity['start'], entity['end']),
                    'description': entity.get('description', '')
                }
            )
            concepts.append(concept)
            
        # Концепты из ключевых слов
        for keyword in processed_text.keywords:
            # Найдем соответствующий токен
            token = next((t for t in processed_text.tokens if t.lemma == keyword), None)
            if token:
                category = self._map_pos_to_category(token.pos)
                concept = Concept(
                    name=keyword,
                    category=category,
                    confidence=0.6,  # Средняя уверенность для ключевых слов
                    attributes={
                        'pos': token.pos,
                        'sentiment': token.sentiment,
                        'frequency': 1  # Упрощенно
                    }
                )
                concepts.append(concept)
                
        # Концепты из тематических групп
        semantic_level = next(level for level in context_analysis.levels if level.name == 'semantic')
        themes = semantic_level.features.get('themes', [])
        
        for theme in themes:
            concept = Concept(
                name=theme,
                category='theme',
                confidence=0.4,  # Низкая уверенность для автоматически выведенных тем
                attributes={
                    'type': 'thematic',
                    'scope': 'document'
                }
            )
            concepts.append(concept)
            
        return concepts
        
    def _extract_relationships(self, concepts: List[Concept], processed_text: ProcessedText) -> List[Relationship]:
        """Извлечение отношений между концептами"""
        relationships = []
        
        # Простые эвристики для отношений
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts):
                if i != j:
                    relation_type, strength = self._infer_relationship(concept1, concept2, processed_text)
                    if strength > 0.1:  # Пороговое значение
                        relationship = Relationship(
                            source=concept1.name,
                            target=concept2.name,
                            relation_type=relation_type,
                            strength=strength
                        )
                        relationships.append(relationship)
                        
        return relationships
        
    def _build_abstraction_hierarchy(self, concepts: List[Concept]) -> Dict[int, List[str]]:
        """Построение иерархии абстракций"""
        hierarchy = {0: [], 1: [], 2: []}
        
        for concept in concepts:
            # Уровень 0: Конкретные сущности
            if concept.category in ['entity', 'PERSON', 'ORG', 'PRODUCT']:
                hierarchy[0].append(concept.name)
            # Уровень 1: Действия и качества
            elif concept.category in ['action', 'quality']:
                hierarchy[1].append(concept.name)
            # Уровень 2: Абстрактные темы
            else:
                hierarchy[2].append(concept.name)
                
        return hierarchy
        
    def _create_semantic_vector(self, concepts: List[Concept], relationships: List[Relationship]) -> np.ndarray:
        """Создание семантического вектора"""
        # Упрощенное векторное представление
        vector = np.zeros(self.vector_dimension)
        
        # Кодируем концепты
        for i, concept in enumerate(concepts):
            if i < self.vector_dimension:
                vector[i] = concept.confidence
                
        # Добавляем информацию об отношениях
        relationship_strength = sum(rel.strength for rel in relationships)
        if len(vector) > len(concepts):
            vector[len(concepts)] = relationship_strength / max(len(relationships), 1)
            
        return vector
        
    def _map_entity_to_category(self, entity_label: str) -> str:
        """Маппинг типа сущности в категорию"""
        for category, labels in self.semantic_categories.items():
            if entity_label in labels:
                return category
        return 'entity'
        
    def _map_pos_to_category(self, pos: str) -> str:
        """Маппинг части речи в категорию"""
        pos_mapping = {
            'NOUN': 'entity',
            'VERB': 'action', 
            'ADJ': 'quality',
            'ADV': 'quality',
            'NUM': 'quantity'
        }
        return pos_mapping.get(pos, 'other')
        
    def _infer_relationship(self, concept1: Concept, concept2: Concept, processed_text: ProcessedText) -> Tuple[str, float]:
        """Вывод отношения между концептами"""
        # Упрощенная логика вывода отношений
        
        # Проверяем близость в тексте
        text_proximity = self._calculate_text_proximity(concept1.name, concept2.name, processed_text.original)
        
        # Определяем тип отношения на основе категорий
        if concept1.category == 'action' and concept2.category == 'entity':
            return 'acts_on', text_proximity * 0.8
        elif concept1.category == 'quality' and concept2.category == 'entity':
            return 'describes', text_proximity * 0.7
        elif concept1.category == concept2.category:
            return 'similar_to', text_proximity * 0.5
        else:
            return 'related_to', text_proximity * 0.3
            
    def _calculate_text_proximity(self, term1: str, term2: str, text: str) -> float:
        """Расчет близости терминов в тексте"""
        text_lower = text.lower()
        pos1 = text_lower.find(term1.lower())
        pos2 = text_lower.find(term2.lower())
        
        if pos1 == -1 or pos2 == -1:
            return 0.0
            
        distance = abs(pos1 - pos2)
        max_distance = len(text)
        
        # Нормализуем: чем ближе, тем выше оценка
        proximity = 1.0 - (distance / max_distance)
        return max(proximity, 0.0)
        
    def _calculate_map_complexity(self, concepts: List[Concept], relationships: List[Relationship]) -> float:
        """Расчет сложности семантической карты"""
        concept_complexity = len(concepts) / 20.0  # Нормализуем к примерно [0, 1]
        relationship_complexity = len(relationships) / 50.0
        
        # Учитываем разнообразие категорий
        unique_categories = len(set(concept.category for concept in concepts))
        category_diversity = unique_categories / 10.0
        
        total_complexity = (concept_complexity + relationship_complexity + category_diversity) / 3.0
        return min(total_complexity, 1.0)