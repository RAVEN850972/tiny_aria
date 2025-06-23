# src/dsl/parser.py
from typing import List, Dict, Any, Optional
from .tokens import Token, TokenType
from .lexer import Lexer

class ASTNode:
    pass

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
        
        return RuleNode(name, condition, action, confidence)