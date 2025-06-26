# src/tests/test_dsl.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import pytest
import sys
import os

# Добавляем пути для импорта
sys.path.insert(0, os.path.abspath('../'))

from src.dsl.lexer import Lexer, TokenType
from src.dsl.parser import Parser
from src.dsl.compiler import DSLCompiler

class TestDSLLexer:
    def test_tokenize_simple_rule(self):
        """Тест токенизации простого правила"""
        dsl_code = '''
        rule "test_rule" {
            if: "hello"
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
        assert TokenType.IF in token_types
        assert TokenType.THEN in token_types
        assert TokenType.COLON in token_types
        assert TokenType.NUMBER in token_types
        
    def test_tokenize_string_literals(self):
        """Тест токенизации строковых литералов"""
        lexer = Lexer('"Hello, world!"')
        tokens = lexer.tokenize()
        
        assert len(tokens) == 2  # STRING + EOF
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "Hello, world!"
        
    def test_tokenize_numbers(self):
        """Тест токенизации чисел"""
        # Целое число
        lexer = Lexer('42')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42
        
        # Десятичное число
        lexer = Lexer('3.14')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 3.14
        
        # Отрицательное число
        lexer = Lexer('-10')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == -10
        
    def test_tokenize_identifiers(self):
        """Тест токенизации идентификаторов"""
        lexer = Lexer('my_variable')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "my_variable"
        
    def test_tokenize_keywords(self):
        """Тест токенизации ключевых слов"""
        keywords = ['rule', 'plugin', 'config', 'if', 'then', 'when']
        
        for keyword in keywords:
            lexer = Lexer(keyword)
            tokens = lexer.tokenize()
            assert tokens[0].type.value == keyword
            
    def test_tokenize_booleans(self):
        """Тест токенизации булевых значений"""
        lexer = Lexer('true false')
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.BOOLEAN
        assert tokens[0].value == True
        
        assert tokens[1].type == TokenType.BOOLEAN
        assert tokens[1].value == False
        
    def test_tokenize_operators(self):
        """Тест токенизации операторов"""
        operators = {
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
        
        for op, expected_type in operators.items():
            lexer = Lexer(op)
            tokens = lexer.tokenize()
            assert tokens[0].type == expected_type
            
    def test_tokenize_comments(self):
        """Тест обработки комментариев"""
        lexer = Lexer('rule # это комментарий\n"test"')
        tokens = lexer.tokenize()
        
        # Комментарии должны быть проигнорированы
        token_types = [token.type for token in tokens]
        assert TokenType.RULE in token_types
        assert TokenType.STRING in token_types
        # Комментарии не должны создавать отдельные токены

class TestDSLParser:
    def test_parse_simple_rule(self):
        """Тест парсинга простого правила"""
        dsl_code = '''
        rule "greeting" {
            if: "hello"
            then: "Hello!"
            confidence: 0.8
        }
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        assert len(ast_nodes) == 1
        rule_node = ast_nodes[0]
        assert rule_node.name == "greeting"
        assert rule_node.confidence == 0.8
        assert rule_node.condition.value == "hello"
        assert rule_node.action.value == "Hello!"
        
    def test_parse_plugin(self):
        """Тест парсинга плагина"""
        dsl_code = '''
        plugin TextProcessor {
            enabled: true
            language: "auto"
            max_tokens: 1000
        }
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        assert len(ast_nodes) == 1
        plugin_node = ast_nodes[0]
        assert plugin_node.name == "TextProcessor"
        assert plugin_node.config["enabled"] == True
        assert plugin_node.config["language"] == "auto"
        assert plugin_node.config["max_tokens"] == 1000
        
    def test_parse_config(self):
        """Тест парсинга конфигурации"""
        dsl_code = '''
        config {
            debug: true
            max_memory: 1024
            timeout: 30.5
        }
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        assert len(ast_nodes) == 1
        config_node = ast_nodes[0]
        assert config_node.settings["debug"] == True
        assert config_node.settings["max_memory"] == 1024
        assert config_node.settings["timeout"] == 30.5
        
    def test_parse_multiple_constructs(self):
        """Тест парсинга нескольких конструкций"""
        dsl_code = '''
        rule "test1" {
            if: "input1"
            then: "output1"
        }
        
        plugin MyPlugin {
            enabled: true
        }
        
        config {
            debug: false
        }
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        assert len(ast_nodes) == 3
        
        # Проверяем типы узлов
        from dsl.parser import RuleNode, PluginNode, ConfigNode
        
        assert isinstance(ast_nodes[0], RuleNode)
        assert isinstance(ast_nodes[1], PluginNode)
        assert isinstance(ast_nodes[2], ConfigNode)
        
    def test_parse_error_handling(self):
        """Тест обработки ошибок парсинга"""
        # Незакрытая скобка
        dsl_code = '''
        rule "test" {
            if: "input"
        # Нет закрывающей скобки
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        
        with pytest.raises(SyntaxError):
            parser.parse()

class TestDSLCompiler:
    def test_compile_simple_rule(self):
        """Тест компиляции простого правила"""
        dsl_code = '''
        rule "test_rule" {
            if: "hello"
            then: "Hello, world!"
            confidence: 0.9
        }
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        compiler = DSLCompiler()
        compiler.compile(ast_nodes)
        
        assert len(compiler.compiled_rules) == 1
        
        rule = compiler.compiled_rules[0]
        assert rule.name == "test_rule"
        assert rule.confidence == 0.9
        
        # Тестируем выполнение правила
        context = {"user_input": "hello"}
        assert rule.evaluate(context) == True
        
        result = rule.execute(context)
        assert result == "Hello, world!"
        
    def test_compile_plugin(self):
        """Тест компиляции плагина"""
        dsl_code = '''
        plugin TestPlugin {
            enabled: true
            setting1: "value1"
            setting2: 42
        }
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        compiler = DSLCompiler()
        compiler.compile(ast_nodes)
        
        assert "TestPlugin" in compiler.plugin_configs
        config = compiler.plugin_configs["TestPlugin"]
        assert config["enabled"] == True
        assert config["setting1"] == "value1"
        assert config["setting2"] == 42
        
    def test_compile_system_config(self):
        """Тест компиляции системной конфигурации"""
        dsl_code = '''
        config {
            debug: true
            max_memory: 1024
            timeout: 30.0
        }
        '''
        
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        compiler = DSLCompiler()
        compiler.compile(ast_nodes)
        
        assert compiler.system_config["debug"] == True
        assert compiler.system_config["max_memory"] == 1024
        assert compiler.system_config["timeout"] == 30.0

if __name__ == "__main__":
    # Для запуска тестов напрямую
    pytest.main([__file__, "-v"])