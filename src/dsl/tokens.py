# src/dsl/tokens.py
from enum import Enum
from dataclasses import dataclass
from typing import Any

class TokenType(Enum):
    # Ключевые слова
    RULE = "rule"
    PLUGIN = "plugin"
    CONFIG = "config"
    IF = "if"
    THEN = "then"
    WHEN = "when"
    
    # Операторы
    COLON = ":"
    SEMICOLON = ";"
    COMMA = ","
    DOT = "."
    
    # Скобки
    LBRACE = "{"
    RBRACE = "}"
    LPAREN = "("
    RPAREN = ")"
    LBRACKET = "["
    RBRACKET = "]"
    
    # Литералы
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    IDENTIFIER = "identifier"
    
    # Специальные
    NEWLINE = "newline"
    EOF = "eof"
    WHITESPACE = "whitespace"

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

