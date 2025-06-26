# src/dsl/parser.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .tokens import Token, TokenType
from .lexer import Lexer

class ASTNode:
    """Базовый класс для узлов AST"""
    pass

@dataclass
class ExpressionNode(ASTNode):
    """Узел выражения"""
    value: Any
    type: str = "literal"

@dataclass
class RuleNode(ASTNode):
    name: str
    condition: 'ExpressionNode'
    action: 'ExpressionNode'
    confidence: float = 1.0

@dataclass  
class PluginNode(ASTNode):
    name: str
    config: Dict[str, Any]

@dataclass
class ConfigNode(ASTNode):
    settings: Dict[str, Any]

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
        
        # Пропускаем пустые токены в начале
        while self.current_token and self.current_token.type == TokenType.WHITESPACE:
            self._advance()
        
    def parse(self) -> List[ASTNode]:
        """Парсинг списка токенов в AST"""
        nodes = []
        
        while not self._is_at_end():
            node = self._parse_top_level()
            if node:
                nodes.append(node)
                
        return nodes
        
    def _parse_top_level(self) -> Optional[ASTNode]:
        """Парсинг конструкций верхнего уровня"""
        if self._match(TokenType.RULE):
            return self._parse_rule()
        elif self._match(TokenType.PLUGIN):
            return self._parse_plugin()
        elif self._match(TokenType.CONFIG):
            return self._parse_config()
        else:
            self._advance()
            return None
            
    def _parse_rule(self) -> RuleNode:
        """Парсинг правила"""
        name = self._consume(TokenType.STRING, "Expected rule name").value
        self._consume(TokenType.LBRACE, "Expected '{'")
        
        condition = None
        action = None
        confidence = 1.0
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._match(TokenType.IF):
                self._consume(TokenType.COLON, "Expected ':'")
                condition = self._parse_expression()
            elif self._match(TokenType.THEN):
                self._consume(TokenType.COLON, "Expected ':'")
                action = self._parse_expression()
            elif self._check(TokenType.IDENTIFIER) and self.current_token.value == "confidence":
                self._advance()
                self._consume(TokenType.COLON, "Expected ':'")
                confidence = self._consume(TokenType.NUMBER, "Expected number").value
                
        self._consume(TokenType.RBRACE, "Expected '}'")
        
        # Создаем простые выражения если не заданы
        if condition is None:
            condition = ExpressionNode(True, "boolean")
        if action is None:
            action = ExpressionNode("No action specified", "string")
        
        return RuleNode(name, condition, action, confidence)
    
    def _parse_plugin(self) -> PluginNode:
        """Парсинг плагина"""
        name = self._consume(TokenType.IDENTIFIER, "Expected plugin name").value
        self._consume(TokenType.LBRACE, "Expected '{'")
        
        config = {}
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            # Простой парсинг конфигурации key: value
            if self._check(TokenType.IDENTIFIER):
                key = self._advance().value
                self._consume(TokenType.COLON, "Expected ':'")
                value = self._parse_simple_value()
                config[key] = value
            else:
                self._advance()  # Пропускаем неизвестные токены
                
        self._consume(TokenType.RBRACE, "Expected '}'")
        return PluginNode(name, config)
    
    def _parse_config(self) -> ConfigNode:
        """Парсинг конфигурации"""
        self._consume(TokenType.LBRACE, "Expected '{'")
        
        settings = {}
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._check(TokenType.IDENTIFIER):
                key = self._advance().value
                self._consume(TokenType.COLON, "Expected ':'")
                value = self._parse_simple_value()
                settings[key] = value
            else:
                self._advance()
                
        self._consume(TokenType.RBRACE, "Expected '}'")
        return ConfigNode(settings)
    
    def _parse_expression(self) -> ExpressionNode:
        """Парсинг выражения"""
        if self._check(TokenType.STRING):
            value = self._advance().value
            return ExpressionNode(value, "string")
        elif self._check(TokenType.NUMBER):
            value = self._advance().value
            return ExpressionNode(value, "number")
        elif self._check(TokenType.BOOLEAN):
            value = self._advance().value
            return ExpressionNode(value, "boolean")
        elif self._check(TokenType.IDENTIFIER):
            value = self._advance().value
            return ExpressionNode(value, "identifier")
        else:
            # Возвращаем выражение по умолчанию
            return ExpressionNode(True, "boolean")
    
    def _parse_simple_value(self) -> Any:
        """Парсинг простого значения"""
        if self._check(TokenType.STRING):
            return self._advance().value
        elif self._check(TokenType.NUMBER):
            return self._advance().value
        elif self._check(TokenType.BOOLEAN):
            return self._advance().value
        elif self._check(TokenType.IDENTIFIER):
            return self._advance().value
        else:
            return None
    
    # Вспомогательные методы
    def _match(self, *types) -> bool:
        """Проверяет, соответствует ли текущий токен одному из типов"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Проверяет тип текущего токена"""
        if self._is_at_end():
            return False
        return self.current_token.type == token_type
    
    def _advance(self) -> Token:
        """Переходит к следующему токену"""
        if not self._is_at_end():
            previous_token = self.current_token
            self.position += 1
            
            # Обновляем текущий токен
            if self.position < len(self.tokens):
                self.current_token = self.tokens[self.position]
                
                # Пропускаем whitespace токены
                while (self.current_token and 
                       self.current_token.type == TokenType.WHITESPACE and 
                       not self._is_at_end()):
                    self.position += 1
                    if self.position < len(self.tokens):
                        self.current_token = self.tokens[self.position]
            else:
                self.current_token = None
            
            return previous_token
        return None
    
    def _is_at_end(self) -> bool:
        """Проверяет, достигнут ли конец токенов"""
        return (self.position >= len(self.tokens) or 
                self.current_token is None or 
                self.current_token.type == TokenType.EOF)
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Потребляет токен определенного типа или выдает ошибку"""
        if self._check(token_type):
            return self._advance()
        
        current = self.current_token.type if self.current_token else "EOF"
        raise SyntaxError(f"{message}. Got {current} at line {self.current_token.line if self.current_token else 'EOF'}")

# Экспортируем все классы
__all__ = ['ASTNode', 'ExpressionNode', 'RuleNode', 'PluginNode', 'ConfigNode', 'Parser']