# src/dsl/lexer.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import re
from typing import List, Iterator
from .tokens import Token, TokenType

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        
        # Ключевые слова
        self.keywords = {
            'rule': TokenType.RULE,
            'plugin': TokenType.PLUGIN,
            'config': TokenType.CONFIG,
            'if': TokenType.IF,
            'then': TokenType.THEN,
            'when': TokenType.WHEN,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN
        }
        
    def tokenize(self) -> List[Token]:
        """Токенизация входного текста"""
        tokens = []
        
        while self.position < len(self.text):
            token = self._next_token()
            if token and token.type != TokenType.WHITESPACE:
                tokens.append(token)
                
        tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return tokens
        
    def _next_token(self) -> Token:
        """Получение следующего токена"""
        if self.position >= len(self.text):
            return None
            
        char = self.text[self.position]
        
        # Пропуск пробелов
        if char.isspace():
            return self._read_whitespace()
            
        # Комментарии
        if char == '#':
            return self._read_comment()
            
        # Строки
        if char in ['"', "'"]:
            return self._read_string()
            
        # Числа
        if char.isdigit() or (char == '-' and self.position + 1 < len(self.text) and self.text[self.position + 1].isdigit()):
            return self._read_number()
            
        # Идентификаторы и ключевые слова
        if char.isalpha() or char == '_':
            return self._read_identifier()
            
        # Операторы и скобки
        return self._read_operator()
        
    def _read_string(self) -> Token:
        """Чтение строкового литерала"""
        quote = self.text[self.position]
        start_pos = self.position
        start_col = self.column
        
        self._advance()  # Пропускаем открывающую кавычку
        
        value = ""
        while self.position < len(self.text) and self.text[self.position] != quote:
            if self.text[self.position] == '\\':
                self._advance()
                if self.position < len(self.text):
                    escape_char = self.text[self.position]
                    if escape_char == 'n':
                        value += '\n'
                    elif escape_char == 't':
                        value += '\t'
                    elif escape_char == 'r':
                        value += '\r'
                    elif escape_char == '\\':
                        value += '\\'
                    elif escape_char == quote:
                        value += quote
                    else:
                        value += escape_char
            else:
                value += self.text[self.position]
            self._advance()
            
        if self.position < len(self.text):
            self._advance()  # Пропускаем закрывающую кавычку
            
        return Token(TokenType.STRING, value, self.line, start_col)
    
    def _read_number(self) -> Token:
        """Чтение числового литерала"""
        start_col = self.column
        value = ""
        
        # Обрабатываем знак минус
        if self.text[self.position] == '-':
            value += '-'
            self._advance()
        
        # Читаем цифры
        while self.position < len(self.text) and self.text[self.position].isdigit():
            value += self.text[self.position]
            self._advance()
            
        # Обрабатываем десятичную точку
        if (self.position < len(self.text) and 
            self.text[self.position] == '.' and 
            self.position + 1 < len(self.text) and 
            self.text[self.position + 1].isdigit()):
            
            value += '.'
            self._advance()
            
            while self.position < len(self.text) and self.text[self.position].isdigit():
                value += self.text[self.position]
                self._advance()
            
            return Token(TokenType.NUMBER, float(value), self.line, start_col)
        else:
            return Token(TokenType.NUMBER, int(value), self.line, start_col)
    
    def _read_identifier(self) -> Token:
        """Чтение идентификатора или ключевого слова"""
        start_col = self.column
        value = ""
        
        while (self.position < len(self.text) and 
               (self.text[self.position].isalnum() or self.text[self.position] == '_')):
            value += self.text[self.position]
            self._advance()
        
        # Проверяем, является ли идентификатор ключевым словом
        token_type = self.keywords.get(value.lower(), TokenType.IDENTIFIER)
        
        # Специальная обработка булевых значений
        if token_type == TokenType.BOOLEAN:
            bool_value = value.lower() == 'true'
            return Token(TokenType.BOOLEAN, bool_value, self.line, start_col)
        else:
            return Token(token_type, value, self.line, start_col)
    
    def _read_operator(self) -> Token:
        """Чтение операторов и пунктуации"""
        start_col = self.column
        char = self.text[self.position]
        
        # Одиночные символы
        single_chars = {
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
        }
        
        if char in single_chars:
            self._advance()
            return Token(single_chars[char], char, self.line, start_col)
        
        # Неизвестный символ - пропускаем
        self._advance()
        return None
    
    def _read_whitespace(self) -> Token:
        """Чтение пробельных символов"""
        start_col = self.column
        
        while self.position < len(self.text) and self.text[self.position].isspace():
            if self.text[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
            
        return Token(TokenType.WHITESPACE, None, self.line, start_col)
    
    def _read_comment(self) -> Token:
        """Чтение комментария"""
        start_col = self.column
        
        # Пропускаем все до конца строки
        while self.position < len(self.text) and self.text[self.position] != '\n':
            self._advance()
            
        return Token(TokenType.WHITESPACE, None, self.line, start_col)  # Комментарии как whitespace
    
    def _advance(self):
        """Переход к следующему символу"""
        if self.position < len(self.text):
            if self.text[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1