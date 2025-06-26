# src/dsl/compiler.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .parser import ExpressionNode

from .parser import ASTNode, RuleNode, PluginNode, ConfigNode

class CompiledRule:
    def __init__(self, name: str, condition_func, action_func, confidence: float):
        self.name = name
        self.condition = condition_func
        self.action = action_func
        self.confidence = confidence
        
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Проверка условия правила"""
        try:
            return self.condition(context)
        except Exception as e:
            print(f"Error evaluating condition for rule {self.name}: {e}")
            return False
        
    def execute(self, context: Dict[str, Any]) -> Any:
        """Выполнение действия правила"""
        try:
            return self.action(context)
        except Exception as e:
            print(f"Error executing action for rule {self.name}: {e}")
            return f"Error in rule {self.name}"

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
        # Компилируем условие
        condition_func = self._compile_condition(rule_node.condition)
        
        # Компилируем действие
        action_func = self._compile_action(rule_node.action)
        
        # Создаем скомпилированное правило
        compiled_rule = CompiledRule(
            rule_node.name,
            condition_func,
            action_func,
            rule_node.confidence
        )
        
        self.compiled_rules.append(compiled_rule)
        
    def _compile_condition(self, condition):
        """Компиляция условия в функцию"""
        if condition.type == "boolean":
            # Простое булево значение
            value = condition.value
            return lambda context: bool(value)
            
        elif condition.type == "string":
            # Проверка содержимости строки в пользовательском вводе
            search_string = condition.value.lower()
            
            def string_condition(context):
                user_input = context.get('user_input', '').lower()
                return search_string in user_input
            
            return string_condition
            
        elif condition.type == "identifier":
            # Проверка значения переменной в контексте
            var_name = condition.value
            
            def identifier_condition(context):
                return bool(context.get(var_name, False))
            
            return identifier_condition
            
        elif condition.type == "number":
            # Числовое условие (всегда истинно если не 0)
            value = condition.value
            return lambda context: bool(value)
            
        else:
            # По умолчанию всегда истинно
            return lambda context: True
            
    def _compile_action(self, action):
        """Компиляция действия в функцию"""
        if action.type == "string":
            # Возвращаем строку как есть
            response = action.value
            return lambda context: response
            
        elif action.type == "identifier":
            # Возвращаем значение переменной из контекста
            var_name = action.value
            
            def identifier_action(context):
                return context.get(var_name, f"Variable {var_name} not found")
            
            return identifier_action
            
        elif action.type == "number":
            # Возвращаем число
            value = action.value
            return lambda context: str(value)
            
        elif action.type == "boolean":
            # Возвращаем булево значение как строку
            value = action.value
            return lambda context: str(value)
            
        else:
            # По умолчанию возвращаем описание действия
            return lambda context: f"Action: {action.value}"
            
    def _compile_plugin(self, plugin_node: PluginNode):
        """Компиляция конфигурации плагина"""
        self.plugin_configs[plugin_node.name] = plugin_node.config.copy()
        
    def _compile_config(self, config_node: ConfigNode):
        """Компиляция системной конфигурации"""
        self.system_config.update(config_node.settings)
        
    def get_rule_by_name(self, name: str) -> CompiledRule:
        """Получение правила по имени"""
        for rule in self.compiled_rules:
            if rule.name == name:
                return rule
        return None
        
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Получение конфигурации плагина"""
        return self.plugin_configs.get(plugin_name, {})
        
    def get_system_config(self) -> Dict[str, Any]:
        """Получение системной конфигурации"""
        return self.system_config.copy()
        
    def execute_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Выполнение всех применимых правил"""
        results = []
        
        for rule in self.compiled_rules:
            if rule.evaluate(context):
                result = rule.execute(context)
                results.append({
                    'rule_name': rule.name,
                    'result': result,
                    'confidence': rule.confidence
                })
                
        # Сортируем по убыванию уверенности
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return results
        
    def clear(self):
        """Очистка всех скомпилированных данных"""
        self.compiled_rules.clear()
        self.plugin_configs.clear()
        self.system_config.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики компилятора"""
        return {
            'rules_count': len(self.compiled_rules),
            'plugins_count': len(self.plugin_configs),
            'config_entries': len(self.system_config),
            'rule_names': [rule.name for rule in self.compiled_rules],
            'plugin_names': list(self.plugin_configs.keys())
        }

# Дополнительные функции для расширенной компиляции условий
class AdvancedConditionCompiler:
    """Расширенный компилятор условий для более сложных выражений"""
    
    @staticmethod
    def compile_contains(text: str, search_term: str):
        """Компиляция условия 'содержит'"""
        def condition(context):
            user_input = context.get('user_input', '').lower()
            return search_term.lower() in user_input
        return condition
    
    @staticmethod
    def compile_equals(variable: str, value: Any):
        """Компиляция условия 'равно'"""
        def condition(context):
            return context.get(variable) == value
        return condition
    
    @staticmethod
    def compile_greater_than(variable: str, threshold: float):
        """Компиляция условия 'больше чем'"""
        def condition(context):
            try:
                var_value = float(context.get(variable, 0))
                return var_value > threshold
            except (ValueError, TypeError):
                return False
        return condition
    
    @staticmethod
    def compile_and_condition(conditions: List):
        """Компиляция условия 'И'"""
        def condition(context):
            return all(cond(context) for cond in conditions)
        return condition
    
    @staticmethod
    def compile_or_condition(conditions: List):
        """Компиляция условия 'ИЛИ'"""
        def condition(context):
            return any(cond(context) for cond in conditions)
        return condition

# Расширенный компилятор действий
class AdvancedActionCompiler:
    """Расширенный компилятор действий для более сложных операций"""
    
    @staticmethod
    def compile_template_response(template: str):
        """Компиляция шаблонного ответа с переменными"""
        def action(context):
            try:
                return template.format(**context)
            except KeyError as e:
                return f"Template error: missing variable {e}"
        return action
    
    @staticmethod
    def compile_function_call(function_name: str, args: List[Any]):
        """Компиляция вызова функции"""
        def action(context):
            # В реальной реализации здесь был бы реестр функций
            if function_name == "get_time":
                import datetime
                return str(datetime.datetime.now())
            elif function_name == "echo":
                return str(args[0]) if args else "No arguments"
            else:
                return f"Unknown function: {function_name}"
        return action
    
    @staticmethod
    def compile_set_variable(variable: str, value: Any):
        """Компиляция установки переменной"""
        def action(context):
            context[variable] = value
            return f"Set {variable} = {value}"
        return action