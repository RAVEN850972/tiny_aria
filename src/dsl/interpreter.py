# src/dsl/interpreter.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from typing import Dict, Any, List
import logging
from .compiler import DSLCompiler

class DSLInterpreter:
    def __init__(self, compiler: DSLCompiler = None):
        self.compiler = compiler or DSLCompiler()
        self.context: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
    def set_context(self, context: Dict[str, Any]):
        """Установка контекста выполнения"""
        self.context.update(context)
        
    def execute_rules(self) -> List[Dict[str, Any]]:
        """Выполнение всех правил"""
        results = []
        
        for rule in self.compiler.compiled_rules:
            try:
                if rule.evaluate(self.context):
                    result = rule.execute(self.context)
                    execution_result = {
                        'rule': rule.name,
                        'result': result,
                        'confidence': rule.confidence,
                        'success': True,
                        'error': None
                    }
                    results.append(execution_result)
                    self.logger.debug(f"Rule {rule.name} executed successfully")
                else:
                    self.logger.debug(f"Rule {rule.name} condition not met")
                    
            except Exception as e:
                error_result = {
                    'rule': rule.name,
                    'result': None,
                    'confidence': 0.0,
                    'success': False,
                    'error': str(e)
                }
                results.append(error_result)
                self.logger.error(f"Error executing rule {rule.name}: {e}")
                
        # Записываем в историю выполнения
        self.execution_history.append({
            'context': self.context.copy(),
            'results': results,
            'timestamp': self._get_timestamp()
        })
        
        return results
        
    def execute_single_rule(self, rule_name: str) -> Dict[str, Any]:
        """Выполнение одного правила по имени"""
        rule = self.compiler.get_rule_by_name(rule_name)
        
        if not rule:
            return {
                'rule': rule_name,
                'result': None,
                'confidence': 0.0,
                'success': False,
                'error': f"Rule '{rule_name}' not found"
            }
            
        try:
            if rule.evaluate(self.context):
                result = rule.execute(self.context)
                return {
                    'rule': rule_name,
                    'result': result,
                    'confidence': rule.confidence,
                    'success': True,
                    'error': None
                }
            else:
                return {
                    'rule': rule_name,
                    'result': None,
                    'confidence': rule.confidence,
                    'success': False,
                    'error': "Rule condition not met"
                }
                
        except Exception as e:
            return {
                'rule': rule_name,
                'result': None,
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
            
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Получение конфигурации плагина"""
        return self.compiler.get_plugin_config(plugin_name)
        
    def get_system_config(self) -> Dict[str, Any]:
        """Получение системной конфигурации"""
        return self.compiler.get_system_config()
        
    def get_applicable_rules(self) -> List[str]:
        """Получение списка применимых правил для текущего контекста"""
        applicable_rules = []
        
        for rule in self.compiler.compiled_rules:
            try:
                if rule.evaluate(self.context):
                    applicable_rules.append(rule.name)
            except Exception as e:
                self.logger.warning(f"Error evaluating rule {rule.name}: {e}")
                
        return applicable_rules
        
    def get_best_rule(self) -> Dict[str, Any]:
        """Получение наилучшего правила для текущего контекста"""
        applicable_results = []
        
        for rule in self.compiler.compiled_rules:
            try:
                if rule.evaluate(self.context):
                    applicable_results.append({
                        'name': rule.name,
                        'confidence': rule.confidence
                    })
            except Exception:
                continue
                
        if not applicable_results:
            return None
            
        # Сортируем по уверенности
        applicable_results.sort(key=lambda x: x['confidence'], reverse=True)
        best_rule_name = applicable_results[0]['name']
        
        return self.execute_single_rule(best_rule_name)
        
    def reset_context(self):
        """Сброс контекста"""
        self.context.clear()
        
    def clear_history(self):
        """Очистка истории выполнения"""
        self.execution_history.clear()
        
    def get_execution_stats(self) -> Dict[str, Any]:
        """Получение статистики выполнения"""
        if not self.execution_history:
            return {
                'total_executions': 0,
                'successful_rules': 0,
                'failed_rules': 0,
                'most_used_rules': [],
                'average_confidence': 0.0
            }
            
        total_executions = len(self.execution_history)
        successful_rules = 0
        failed_rules = 0
        rule_usage = {}
        confidence_scores = []
        
        for execution in self.execution_history:
            for result in execution['results']:
                if result['success']:
                    successful_rules += 1
                    confidence_scores.append(result['confidence'])
                else:
                    failed_rules += 1
                    
                rule_name = result['rule']
                rule_usage[rule_name] = rule_usage.get(rule_name, 0) + 1
                
        # Наиболее используемые правила
        most_used_rules = sorted(rule_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Средняя уверенность
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            'total_executions': total_executions,
            'successful_rules': successful_rules,
            'failed_rules': failed_rules,
            'most_used_rules': most_used_rules,
            'average_confidence': average_confidence,
            'context_size': len(self.context),
            'available_rules': len(self.compiler.compiled_rules)
        }
        
    def debug_rule(self, rule_name: str) -> Dict[str, Any]:
        """Отладочная информация о правиле"""
        rule = self.compiler.get_rule_by_name(rule_name)
        
        if not rule:
            return {'error': f"Rule '{rule_name}' not found"}
            
        try:
            condition_result = rule.evaluate(self.context)
        except Exception as e:
            condition_result = f"Error: {e}"
            
        return {
            'rule_name': rule.name,
            'confidence': rule.confidence,
            'condition_result': condition_result,
            'context_keys': list(self.context.keys()),
            'context_size': len(self.context)
        }
        
    def validate_rules(self) -> Dict[str, Any]:
        """Валидация всех правил"""
        validation_results = []
        
        for rule in self.compiler.compiled_rules:
            try:
                # Тестируем с пустым контекстом
                empty_context = {}
                condition_works = True
                action_works = True
                
                try:
                    rule.evaluate(empty_context)
                except Exception as e:
                    condition_works = False
                    
                try:
                    rule.execute(empty_context)
                except Exception as e:
                    action_works = False
                    
                validation_results.append({
                    'rule_name': rule.name,
                    'condition_works': condition_works,
                    'action_works': action_works,
                    'confidence': rule.confidence,
                    'valid': condition_works and action_works
                })
                
            except Exception as e:
                validation_results.append({
                    'rule_name': rule.name,
                    'condition_works': False,
                    'action_works': False,
                    'confidence': rule.confidence,
                    'valid': False,
                    'error': str(e)
                })
                
        valid_rules = sum(1 for r in validation_results if r['valid'])
        total_rules = len(validation_results)
        
        return {
            'total_rules': total_rules,
            'valid_rules': valid_rules,
            'invalid_rules': total_rules - valid_rules,
            'validation_rate': valid_rules / total_rules if total_rules > 0 else 0.0,
            'results': validation_results
        }
        
    def _get_timestamp(self) -> float:
        """Получение текущего времени"""
        import time
        return time.time()

# Расширенный интерпретатор с дополнительными возможностями
class AdvancedDSLInterpreter(DSLInterpreter):
    """Расширенный интерпретатор с поддержкой условного выполнения и циклов"""
    
    def __init__(self, compiler: DSLCompiler = None):
        super().__init__(compiler)
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, callable] = {}
        self._setup_builtin_functions()
        
    def _setup_builtin_functions(self):
        """Настройка встроенных функций"""
        self.functions['print'] = lambda *args: print(*args)
        self.functions['len'] = len
        self.functions['str'] = str
        self.functions['int'] = int
        self.functions['float'] = float
        
    def set_variable(self, name: str, value: Any):
        """Установка переменной"""
        self.variables[name] = value
        self.context[name] = value
        
    def get_variable(self, name: str, default=None):
        """Получение переменной"""
        return self.variables.get(name, default)
        
    def register_function(self, name: str, func: callable):
        """Регистрация пользовательской функции"""
        self.functions[name] = func
        
    def execute_conditional(self, condition_rule: str, true_rules: List[str], false_rules: List[str] = None) -> Dict[str, Any]:
        """Условное выполнение правил"""
        condition_result = self.execute_single_rule(condition_rule)
        
        if condition_result['success'] and condition_result['result']:
            # Выполняем правила для true ветки
            results = []
            for rule_name in true_rules:
                result = self.execute_single_rule(rule_name)
                results.append(result)
            return {'branch': 'true', 'results': results}
        else:
            # Выполняем правила для false ветки
            if false_rules:
                results = []
                for rule_name in false_rules:
                    result = self.execute_single_rule(rule_name)
                    results.append(result)
                return {'branch': 'false', 'results': results}
            else:
                return {'branch': 'false', 'results': []}
                
    def execute_loop(self, rule_names: List[str], max_iterations: int = 10) -> List[Dict[str, Any]]:
        """Выполнение правил в цикле"""
        all_results = []
        
        for iteration in range(max_iterations):
            iteration_results = []
            all_applicable = True
            
            for rule_name in rule_names:
                result = self.execute_single_rule(rule_name)
                iteration_results.append(result)
                
                if not (result['success'] and result['result']):
                    all_applicable = False
                    
            all_results.append({
                'iteration': iteration,
                'results': iteration_results,
                'all_applicable': all_applicable
            })
            
            # Прерываем цикл, если ни одно правило не применимо
            if not all_applicable:
                break
                
        return all_results