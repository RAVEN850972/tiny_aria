# src/tests/test_dsl.py
import pytest
from src.dsl.lexer import Lexer, TokenType
from src.dsl.parser import Parser
from src.dsl.compiler import DSLCompiler

class TestDSLLexer:
    def test_tokenize_simple_rule(self):
        """Тест токенизации простого правила"""
        dsl_code = '''
        rule "test_rule" {
            if: user_input == "hello"
            then: "Hello, world!"
            confidence: 0.9
        }
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        # Проверяем наличие основных токенов
        token_types = [token.type for token in tokens]
        assert TokenType.RULE in token_types
        assert TokenType.STRING in token_types
        assert TokenType.LBRACE in token_types
        assert TokenType.RBRACE in token_types
        
    def test_tokenize_string_literals(self):
        """Тест токенизации строковых литералов"""
        lexer = Lexer('"Hello, world!"')
        tokens = lexer.tokenize()
        
        assert len(tokens) == 2  # STRING + EOF
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "Hello, world!"

class TestDSLParser:
    def test_parse_simple_rule(self):
        """Тест парсинга простого правила"""
        dsl_code = '''
        rule "greeting" {
            if: true
            then: "Hello!"
        }
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        assert len(ast_nodes) == 1
        assert ast_nodes[0].name == "greeting"