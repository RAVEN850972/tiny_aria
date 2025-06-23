# src/dsl/compiler.py
from typing import Dict, Any, List
from .parser import ASTNode, RuleNode, PluginNode, ConfigNode

class CompiledRule:
    def __init__(self, name: str, condition_func, action_func, confidence: float):
        self.name = name
        self.condition = condition_func
        self.action = action_func
        self.confidence = confidence
        
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Проверка условия правила"""
        return self.condition(context)
        
    def execute(self, context: Dict[str, Any]) -> Any:
        """Выполнение действия правила"""
        return self.action(context)

class DSLCompiler:
    def __init__(self):
        self.compiled_rules: List[CompiledRule] = []
        self.plugin_configs: Dict[str, Dict] = {}
        self.system_config: Dict[str, Any] = {}
        
    def compile(self, ast_nodes: List[ASTNode]):
        """Компиляция AST в исполняемый код"""
        for node in ast_nodes:
            if isinstance(node, RuleNode):
                self._compile_rule(node)
            elif isinstance(node, PluginNode):
                self._compile_plugin(node)
            elif isinstance(node, ConfigNode):
                self._compile_config(node)
                
    def _compile_rule(self, rule_node: RuleNode):
        """Компиляция правила"""
        # Простая компиляция условий и действий в лямбда-функции
        condition_code = self._compile_expression(rule_node.condition)
        action_code = self._compile_expression(rule_node.action)
        
        # Создаем исполняемые функции
        condition_func = eval(f"lambda context: {condition_code}")
        action_func = eval(f"lambda context: {action_code}")
        
        compiled_rule = CompiledRule(
            rule_node.name,
            condition_func,
            action_func,
            rule_node.confidence
        )
        
        self.compiled_rules.append(compiled_rule)
        
    def _compile_expression(self, expr) -> str:
        """Компиляция выражения в Python код"""
        # Упрощенная реализация
        if hasattr(expr, 'value'):
            return repr(expr.value)
        elif hasattr(expr, 'name'):
            return f"context.get('{expr.name}')"
        else:
            return "True"