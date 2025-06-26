# src/layers/perception/context_analyzer.py
from typing import List, Dict, Any
from dataclasses import dataclass
from .text_processor import ProcessedText, TokenInfo

@dataclass
class ContextLevel:
    name: str
    features: Dict[str, Any]
    confidence: float
    processing_time: float

@dataclass
class ContextAnalysis:
    levels: List[ContextLevel]
    overall_confidence: float
    primary_intent: str
    emotional_tone: str
    complexity_level: str

class ContextAnalyzer:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.context_levels = self.config.get('context_levels', 3)
        
    def analyze(self, processed_text: ProcessedText) -> ContextAnalysis:
        """Анализ контекста на трех уровнях"""
        levels = []
        
        # Уровень 1: Лексический анализ
        lexical_level = self._analyze_lexical(processed_text)
        levels.append(lexical_level)
        
        # Уровень 2: Синтаксический анализ
        syntactic_level = self._analyze_syntactic(processed_text)
        levels.append(syntactic_level)
        
        # Уровень 3: Семантический анализ
        semantic_level = self._analyze_semantic(processed_text)
        levels.append(semantic_level)
        
        # Общая оценка уверенности
        overall_confidence = sum(level.confidence for level in levels) / len(levels)
        
        # Определение основного намерения
        primary_intent = self._determine_intent(processed_text, levels)
        
        # Определение эмоционального тона
        emotional_tone = self._determine_emotional_tone(processed_text)
        
        # Определение уровня сложности
        complexity_level = self._determine_complexity_level(processed_text)
        
        return ContextAnalysis(
            levels=levels,
            overall_confidence=overall_confidence,
            primary_intent=primary_intent,
            emotional_tone=emotional_tone,
            complexity_level=complexity_level
        )
        
    def _analyze_lexical(self, processed_text: ProcessedText) -> ContextLevel:
        """Лексический анализ - значения отдельных слов"""
        import time
        start_time = time.time()
        
        features = {}
        
        # Анализ частей речи
        pos_counts = {}
        for token in processed_text.tokens:
            if token.pos in pos_counts:
                pos_counts[token.pos] += 1
            else:
                pos_counts[token.pos] = 1
                
        features['pos_distribution'] = pos_counts
        features['total_tokens'] = len(processed_text.tokens)
        features['unique_tokens'] = len(set(token.lemma for token in processed_text.tokens))
        features['lexical_diversity'] = features['unique_tokens'] / max(features['total_tokens'], 1)
        
        # Анализ именованных сущностей
        entity_types = {}
        for entity in processed_text.entities:
            entity_type = entity['label']
            if entity_type in entity_types:
                entity_types[entity_type] += 1
            else:
                entity_types[entity_type] = 1
                
        features['entity_distribution'] = entity_types
        features['entity_count'] = len(processed_text.entities)
        
        # Ключевые слова
        features['keywords'] = processed_text.keywords
        features['keyword_count'] = len(processed_text.keywords)
        
        # Простая оценка уверенности на основе полноты анализа
        confidence = 0.8 if processed_text.language in ['en', 'ru'] else 0.5
        
        processing_time = time.time() - start_time
        
        return ContextLevel(
            name="lexical",
            features=features,
            confidence=confidence,
            processing_time=processing_time
        )
        
    def _analyze_syntactic(self, processed_text: ProcessedText) -> ContextLevel:
        """Синтаксический анализ - грамматическая структура"""
        import time
        start_time = time.time()
        
        features = {}
        
        # Анализ зависимостей
        dep_counts = {}
        for token in processed_text.tokens:
            if hasattr(token, 'dep') and token.dep:
                if token.dep in dep_counts:
                    dep_counts[token.dep] += 1
                else:
                    dep_counts[token.dep] = 1
                    
        features['dependency_distribution'] = dep_counts
        
        # Анализ структуры предложений
        features['sentence_count'] = len(processed_text.sentences)
        if processed_text.sentences:
            sentence_lengths = [len(s.split()) for s in processed_text.sentences]
            features['avg_sentence_length'] = sum(sentence_lengths) / len(sentence_lengths)
            features['max_sentence_length'] = max(sentence_lengths)
            features['min_sentence_length'] = min(sentence_lengths)
        else:
            features['avg_sentence_length'] = 0
            features['max_sentence_length'] = 0
            features['min_sentence_length'] = 0
            
        # Сложность синтаксиса
        features['syntactic_complexity'] = self._calculate_syntactic_complexity(processed_text)
        
        # Уверенность зависит от наличия синтаксической информации
        confidence = 0.7 if any(token.dep != 'UNKNOWN' for token in processed_text.tokens) else 0.3
        
        processing_time = time.time() - start_time
        
        return ContextLevel(
            name="syntactic",
            features=features,
            confidence=confidence,
            processing_time=processing_time
        )
        
    def _analyze_semantic(self, processed_text: ProcessedText) -> ContextLevel:
        """Семантический анализ - смысловое содержание"""
        import time
        start_time = time.time()
        
        features = {}
        
        # Тематические группы слов (упрощенная реализация)
        themes = self._identify_themes(processed_text)
        features['themes'] = themes
        
        # Анализ тональности
        features['sentiment_score'] = processed_text.sentiment
        features['sentiment_label'] = self._classify_sentiment(processed_text.sentiment)
        
        # Анализ вопросительности
        features['is_question'] = self._is_question(processed_text)
        
        # Анализ императивности (команды)
        features['is_command'] = self._is_command(processed_text)
        
        # Семантическая связанность
        features['semantic_coherence'] = self._calculate_semantic_coherence(processed_text)
        
        # Абстрактность vs конкретность
        features['abstractness'] = self._calculate_abstractness(processed_text)
        
        confidence = 0.6  # Семантический анализ сложнее, меньше уверенности
        
        processing_time = time.time() - start_time
        
        return ContextLevel(
            name="semantic",
            features=features,
            confidence=confidence,
            processing_time=processing_time
        )
        
    def _calculate_syntactic_complexity(self, processed_text: ProcessedText) -> float:
        """Расчет синтаксической сложности"""
        # Простая метрика на основе разнообразия зависимостей
        unique_deps = set(token.dep for token in processed_text.tokens if hasattr(token, 'dep'))
        dep_diversity = len(unique_deps) / max(len(processed_text.tokens), 1)
        return min(dep_diversity * 2, 1.0)  # Нормализуем к [0, 1]
        
    def _identify_themes(self, processed_text: ProcessedText) -> List[str]:
        """Упрощенная идентификация тем"""
        # Простая категоризация по ключевым словам
        tech_words = {'computer', 'software', 'programming', 'code', 'компьютер', 'программа'}
        emotion_words = {'happy', 'sad', 'angry', 'joy', 'счастливый', 'грустный'}
        question_words = {'what', 'how', 'why', 'when', 'where', 'что', 'как', 'почему'}
        
        themes = []
        keywords_lower = [kw.lower() for kw in processed_text.keywords]
        
        if any(word in keywords_lower for word in tech_words):
            themes.append('technology')
        if any(word in keywords_lower for word in emotion_words):
            themes.append('emotions')
        if any(word in keywords_lower for word in question_words):
            themes.append('inquiry')
            
        return themes if themes else ['general']
        
    def _classify_sentiment(self, sentiment_score: float) -> str:
        """Классификация тональности"""
        if sentiment_score > 0.3:
            return 'positive'
        elif sentiment_score < -0.3:
            return 'negative'
        else:
            return 'neutral'
            
    def _is_question(self, processed_text: ProcessedText) -> bool:
        """Определение вопросительности"""
        text = processed_text.original.lower()
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who', 
                             'что', 'как', 'почему', 'когда', 'где', 'кто']
        return any(indicator in text for indicator in question_indicators)
        
    def _is_command(self, processed_text: ProcessedText) -> bool:
        """Определение императивности"""
        # Простая эвристика: наличие глаголов в императиве
        imperative_indicators = ['please', 'do', 'make', 'create', 'помоги', 'сделай', 'создай']
        text = processed_text.original.lower()
        return any(indicator in text for indicator in imperative_indicators)
        
    def _calculate_semantic_coherence(self, processed_text: ProcessedText) -> float:
        """Расчет семантической связанности"""
        # Упрощенная метрика: отношение ключевых слов к общему количеству слов
        if not processed_text.tokens:
            return 0.0
        coherence = len(processed_text.keywords) / len(processed_text.tokens)
        return min(coherence * 3, 1.0)  # Нормализуем
        
    def _calculate_abstractness(self, processed_text: ProcessedText) -> float:
        """Расчет уровня абстрактности"""
        # Простая эвристика: отношение абстрактных слов к конкретным
        abstract_pos = ['ADJ', 'ADV']  # Прилагательные и наречия часто более абстрактны
        concrete_pos = ['NOUN', 'PROPN']  # Существительные часто более конкретны
        
        abstract_count = sum(1 for token in processed_text.tokens if token.pos in abstract_pos)
        concrete_count = sum(1 for token in processed_text.tokens if token.pos in concrete_pos)
        
        total_relevant = abstract_count + concrete_count
        if total_relevant == 0:
            return 0.5  # Нейтральный уровень
            
        return abstract_count / total_relevant
        
    def _determine_intent(self, processed_text: ProcessedText, levels: List[ContextLevel]) -> str:
        """Определение основного намерения"""
        # Анализируем семантический уровень
        semantic_features = next(level.features for level in levels if level.name == 'semantic')
        
        if semantic_features.get('is_question', False):
            return 'question'
        elif semantic_features.get('is_command', False):
            return 'command'
        elif 'emotions' in semantic_features.get('themes', []):
            return 'emotional_expression'
        elif 'technology' in semantic_features.get('themes', []):
            return 'technical_discussion'
        else:
            return 'general_statement'
            
    def _determine_emotional_tone(self, processed_text: ProcessedText) -> str:
        """Определение эмоционального тона"""
        sentiment = processed_text.sentiment
        
        if sentiment > 0.5:
            return 'very_positive'
        elif sentiment > 0.1:
            return 'positive'
        elif sentiment < -0.5:
            return 'very_negative'
        elif sentiment < -0.1:
            return 'negative'
        else:
            return 'neutral'
            
    def _determine_complexity_level(self, processed_text: ProcessedText) -> str:
        """Определение уровня сложности"""
        complexity = processed_text.complexity
        
        if complexity > 0.7:
            return 'high'
        elif complexity > 0.4:
            return 'medium'
        else:
            return 'low'
