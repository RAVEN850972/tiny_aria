# src/dsl/lexer.py
import re
from typing import List, Iterator
from .tokens import Token, TokenType

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        
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
        if char.isdigit():
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
                    else:
                        value += escape_char
            else:
                value += self.text[self.position]
            self._advance()
            
        if self.position < len(self.text):
            self._advance()  # Пропускаем закрывающую кавычку
            
        return Token(TokenType.STRING, value, self.line, start_col)