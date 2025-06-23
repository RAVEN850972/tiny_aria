# src/dsl/interpreter.py
from typing import Dict, Any, List
import logging

class DSLInterpreter:
    def __init__(self, compiler: DSLCompiler):
        self.compiler = compiler
        self.context: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    def set_context(self, context: Dict[str, Any]):
        """Установка контекста выполнения"""
        self.context.update(context)
        
    def execute_rules(self) -> List[Any]:
        """Выполнение всех правил"""
        results = []
        
        for rule in self.compiler.compiled_rules:
            try:
                if rule.evaluate(self.context):
                    result = rule.execute(self.context)
                    results.append({
                        'rule': rule.name,
                        'result': result,
                        'confidence': rule.confidence
                    })
                    self.logger.debug(f"Rule {rule.name} executed successfully")
                    
            except Exception as e:
                self.logger.error(f"Error executing rule {rule.name}: {e}")
                
        return results
        
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Получение конфигурации плагина"""
        return self.compiler.plugin_configs.get(plugin_name, {})