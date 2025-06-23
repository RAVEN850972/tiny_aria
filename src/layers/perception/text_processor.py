# src/layers/perception/text_processor.py
import re
import nltk
from typing import List, Dict, Any
from dataclasses import dataclass
import spacy

# Загружаем языковые модели при первом импорте
try:
    nlp_en = spacy.load("en_core_web_sm")
except OSError:
    print("English model not found. Install with: python -m spacy download en_core_web_sm")
    nlp_en = None

try:
    nlp_ru = spacy.load("ru_core_news_sm")
except OSError:
    print("Russian model not found. Install with: python -m spacy download ru_core_news_sm")
    nlp_ru = None

@dataclass
class TokenInfo:
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    is_alpha: bool
    is_stop: bool
    sentiment: float = 0.0

@dataclass
class ProcessedText:
    original: str
    language: str
    tokens: List[TokenInfo]
    entities: List[Dict[str, Any]]
    sentences: List[str]
    keywords: List[str]
    sentiment: float
    complexity: float

class TextProcessor:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_tokens = self.config.get('max_tokens', 1000)
        
        # Инициализация NLTK ресурсов
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
    def process(self, text: str) -> ProcessedText:
        """Основная функция обработки текста"""
        if len(text.split()) > self.max_tokens:
            text = ' '.join(text.split()[:self.max_tokens])
            
        # Определение языка
        language = self._detect_language(text)
        
        # Выбор языковой модели
        nlp = self._get_language_model(language)
        
        if nlp is None:
            # Fallback на простую обработку
            return self._simple_processing(text, language)
            
        # Полная обработка с spaCy
        doc = nlp(text)
        
        # Извлечение токенов
        tokens = []
        for token in doc:
            token_info = TokenInfo(
                text=token.text,
                lemma=token.lemma_,
                pos=token.pos_,
                tag=token.tag_,
                dep=token.dep_,
                is_alpha=token.is_alpha,
                is_stop=token.is_stop,
                sentiment=self._get_token_sentiment(token)
            )
            tokens.append(token_info)
            
        # Извлечение именованных сущностей
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'description': spacy.explain(ent.label_)
            })
            
        # Разбиение на предложения
        sentences = [sent.text.strip() for sent in doc.sents]
        
        # Извлечение ключевых слов
        keywords = self._extract_keywords(tokens)
        
        # Анализ тональности
        sentiment = self._analyze_sentiment(tokens)
        
        # Оценка сложности
        complexity = self._calculate_complexity(tokens, sentences)
        
        return ProcessedText(
            original=text,
            language=language,
            tokens=tokens,
            entities=entities,
            sentences=sentences,
            keywords=keywords,
            sentiment=sentiment,
            complexity=complexity
        )
        
    def _detect_language(self, text: str) -> str:
        """Простое определение языка"""
        # Упрощенная эвристика по характерным символам
        cyrillic_chars = len(re.findall(r'[а-яё]', text.lower()))
        latin_chars = len(re.findall(r'[a-z]', text.lower()))
        
        if cyrillic_chars > latin_chars:
            return 'ru'
        else:
            return 'en'
            
    def _get_language_model(self, language: str):
        """Получение языковой модели"""
        if language == 'ru' and nlp_ru:
            return nlp_ru
        elif language == 'en' and nlp_en:
            return nlp_en
        else:
            return None
            
    def _simple_processing(self, text: str, language: str) -> ProcessedText:
        """Упрощенная обработка без spaCy"""
        # Простая токенизация
        words = text.split()
        tokens = []
        
        for word in words:
            # Очистка от пунктуации
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word:
                token_info = TokenInfo(
                    text=word,
                    lemma=clean_word.lower(),
                    pos='UNKNOWN',
                    tag='UNKNOWN',
                    dep='UNKNOWN',
                    is_alpha=clean_word.isalpha(),
                    is_stop=False  # Без spaCy сложно определить
                )
                tokens.append(token_info)
                
        # Простое разбиение на предложения
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return ProcessedText(
            original=text,
            language=language,
            tokens=tokens,
            entities=[],
            sentences=sentences,
            keywords=[],
            sentiment=0.0,
            complexity=len(words) / 10.0  # Простая метрика
        )
        
    def _get_token_sentiment(self, token) -> float:
        """Простая оценка тональности токена"""
        # Упрощенная реализация
        positive_words = {'good', 'great', 'excellent', 'wonderful', 'хорошо', 'отлично'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'плохо', 'ужасно'}
        
        text = token.text.lower()
        if text in positive_words:
            return 1.0
        elif text in negative_words:
            return -1.0
        else:
            return 0.0
            
    def _extract_keywords(self, tokens: List[TokenInfo]) -> List[str]:
        """Извлечение ключевых слов"""
        keywords = []
        
        for token in tokens:
            # Простые эвристики для ключевых слов
            if (token.is_alpha and 
                not token.is_stop and 
                len(token.text) > 3 and
                token.pos in ['NOUN', 'ADJ', 'VERB']):
                keywords.append(token.lemma)
                
        # Удаляем дубликаты, сохраняя порядок
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
                
        return unique_keywords[:10]  # Максимум 10 ключевых слов
        
    def _analyze_sentiment(self, tokens: List[TokenInfo]) -> float:
        """Анализ общей тональности"""
        if not tokens:
            return 0.0
            
        total_sentiment = sum(token.sentiment for token in tokens)
        return total_sentiment / len(tokens)
        
    def _calculate_complexity(self, tokens: List[TokenInfo], sentences: List[str]) -> float:
        """Расчет сложности текста"""
        if not tokens or not sentences:
            return 0.0
            
        # Средняя длина предложения
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Доля сложных слов (длиннее 6 символов)
        complex_words = sum(1 for token in tokens if len(token.text) > 6)
        complex_ratio = complex_words / len(tokens)
        
        # Простая формула сложности
        complexity = (avg_sentence_length / 20.0) + complex_ratio
        
        return min(complexity, 1.0)  # Нормализуем к [0, 1]