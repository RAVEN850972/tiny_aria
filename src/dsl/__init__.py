# src/dsl/__init__.py
"""
DSL (Domain Specific Language) модуль для TinyARIA

Этот модуль предоставляет простой предметно-ориентированный язык
для конфигурации поведения TinyARIA системы.

Основные компоненты:
- Lexer: лексический анализатор для токенизации DSL кода
- Parser: синтаксический анализатор для построения AST
- Compiler: компилятор для преобразования AST в исполняемый код
- Interpreter: интерпретатор для выполнения скомпилированных правил
"""

from .tokens import Token, TokenType
from .lexer import Lexer
from .parser import Parser, ASTNode, RuleNode, PluginNode, ConfigNode
# ExpressionNode импортируется отдельно, так как он определен в parser
try:
    from .parser import ExpressionNode
except ImportError:
    # ExpressionNode может быть не экспортирован из parser
    ExpressionNode = None
from .compiler import DSLCompiler, CompiledRule
try:
    from .compiler import AdvancedConditionCompiler, AdvancedActionCompiler
except ImportError:
    # Расширенные компиляторы могут быть недоступны
    pass
from .interpreter import DSLInterpreter, AdvancedDSLInterpreter
from typing import Dict, Any, List, TYPE_CHECKING

__version__ = "0.1.0"
__author__ = "TinyARIA Team"

__all__ = [
    # Токены
    'Token',
    'TokenType',
    
    # Лексер
    'Lexer',
    
    # Парсер и AST
    'Parser',
    'ASTNode',
    'RuleNode', 
    'PluginNode',
    'ConfigNode',
    
    # Компилятор
    'DSLCompiler',
    'CompiledRule',
    
    # Интерпретатор
    'DSLInterpreter',
    'AdvancedDSLInterpreter',
]

def create_dsl_pipeline():
    """
    Создает полный пайплайн обработки DSL: лексер -> парсер -> компилятор -> интерпретатор
    
    Returns:
        tuple: (lexer_class, parser_class, compiler, interpreter)
    """
    compiler = DSLCompiler()
    interpreter = DSLInterpreter(compiler)
    
    return Lexer, Parser, compiler, interpreter

def compile_dsl_code(dsl_code: str) -> DSLInterpreter:
    """
    Удобная функция для компиляции DSL кода в один вызов
    
    Args:
        dsl_code: Строка с DSL кодом
        
    Returns:
        DSLInterpreter: Готовый к использованию интерпретатор
        
    Example:
        >>> interpreter = compile_dsl_code('''
        ... rule "greeting" {
        ...     if: "hello"
        ...     then: "Hello, world!"
        ...     confidence: 0.9
        ... }
        ... ''')
        >>> context = {"user_input": "hello there"}
        >>> results = interpreter.execute_rules()
    """
    # Лексический анализ
    lexer = Lexer(dsl_code)
    tokens = lexer.tokenize()
    
    # Синтаксический анализ
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    # Компиляция
    compiler = DSLCompiler()
    compiler.compile(ast_nodes)
    
    # Создание интерпретатора
    interpreter = DSLInterpreter(compiler)
    
    return interpreter

def validate_dsl_syntax(dsl_code: str) -> Dict[str, Any]:
    """
    Проверка синтаксиса DSL кода без выполнения
    
    Args:
        dsl_code: Строка с DSL кодом
        
    Returns:
        dict: Результат валидации с информацией об ошибках
    """
    try:
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        compiler = DSLCompiler()
        compiler.compile(ast_nodes)
        
        return {
            'valid': True,
            'error': None,
            'tokens_count': len(tokens),
            'ast_nodes_count': len(ast_nodes),
            'rules_count': len(compiler.compiled_rules),
            'plugins_count': len(compiler.plugin_configs)
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

# Примеры использования DSL
EXAMPLE_RULES = '''
# Пример базовых правил для TinyARIA

rule "greeting_response" {
    if: "hello"
    then: "Здравствуйте! Как дела?"
    confidence: 0.9
}

rule "farewell_response" {
    if: "goodbye"
    then: "До свидания! Хорошего дня!"
    confidence: 0.9
}

rule "help_request" {
    if: "help"
    then: "Я могу помочь вам с различными вопросами. Просто задайте свой вопрос!"
    confidence: 0.8
}

plugin TextProcessor {
    enabled: true
    language: "auto"
    max_tokens: 1000
}

config {
    debug: true
    max_memory: 1024
    timeout: 30
}
'''

if __name__ == "__main__":
    # Демонстрация работы DSL
    print("TinyARIA DSL Demo")
    print("=" * 50)
    
    # Компилируем примеры правил
    interpreter = compile_dsl_code(EXAMPLE_RULES)
    
    # Тестируем различные входы
    test_inputs = [
        "hello there!",
        "help me please", 
        "goodbye for now",
        "random input"
    ]
    
    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        
        interpreter.set_context({"user_input": user_input})
        results = interpreter.execute_rules()
        
        if results:
            best_result = max(results, key=lambda x: x['confidence'])
            print(f"Response: {best_result['result']}")
            print(f"Rule: {best_result['rule']} (confidence: {best_result['confidence']})")
        else:
            print("No applicable rules found")
    
    # Показываем статистику
    print(f"\nCompiler stats: {interpreter.compiler.get_stats()}")