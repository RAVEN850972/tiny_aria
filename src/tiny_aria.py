# src/tiny_aria.py
import logging
from typing import Dict, Any, List
from .core.message_bus import MessageBus, Message, MessageType
from .core.plugin_manager import PluginManager
from .core.config_manager import ConfigManager
from .core.lifecycle_manager import LifecycleManager
from .dsl.lexer import Lexer
from .dsl.parser import Parser
from .dsl.compiler import DSLCompiler
from .dsl.interpreter import DSLInterpreter
from datetime import datetime
import os

class TinyARIA:
    def __init__(self, config_path: str = "config"):
        self.config_manager = ConfigManager(config_path)
        self.message_bus = MessageBus()
        self.plugin_manager = PluginManager()
        self.lifecycle_manager = LifecycleManager()
        self.dsl_compiler = DSLCompiler()
        self.dsl_interpreter = DSLInterpreter(self.dsl_compiler)
        
        self.layers = {}
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Настройка системы логирования"""
        # Создаем директорию logs если её нет
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/tiny_aria.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
        
    def initialize(self, environment: str = "development") -> bool:
        """Инициализация системы"""
        try:
            # Загрузка конфигурации
            self.config_manager.load_config(environment)
            
            # Настройка хуков жизненного цикла
            self.lifecycle_manager.add_initialization_hook(self._init_message_bus)
            self.lifecycle_manager.add_initialization_hook(self._init_plugins)
            self.lifecycle_manager.add_initialization_hook(self._init_layers)
            self.lifecycle_manager.add_initialization_hook(self._load_dsl_config)
            
            self.lifecycle_manager.add_shutdown_hook(self._shutdown_layers)
            self.lifecycle_manager.add_shutdown_hook(self._shutdown_plugins)
            self.lifecycle_manager.add_shutdown_hook(self._shutdown_message_bus)
            
            # Запуск инициализации
            return self.lifecycle_manager.initialize()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TinyARIA: {e}")
            return False
            
    def _init_message_bus(self):
        """Инициализация шины сообщений"""
        self.logger.info("Initializing message bus")
        # Подписка на системные сообщения
        self.message_bus.subscribe(MessageType.ERROR, self._handle_error)
        self.message_bus.subscribe(MessageType.METRIC, self._handle_metric)
        
    def _init_plugins(self):
        """Инициализация плагинов"""
        self.logger.info("Initializing plugins")
        plugins = self.plugin_manager.discover_plugins()
        
        for plugin_name in plugins:
            if self.plugin_manager.load_plugin(plugin_name):
                self.logger.info(f"Plugin {plugin_name} loaded")
            else:
                self.logger.warning(f"Failed to load plugin {plugin_name}")
                
    def _init_layers(self):
        """Инициализация когнитивных слоев"""
        self.logger.info("Initializing cognitive layers")
        
        # Будем импортировать слои по мере их создания
        try:
            # Пытаемся импортировать из разных мест
            try:
                from .layers.perception_layer import PerceptionLayer
            except ImportError:
                from .layers.perception import PerceptionLayer
            
            self.layers['perception'] = PerceptionLayer(
                self.message_bus, 
                self.config_manager.get('perception', {})
            )
            self.logger.info("Perception layer initialized")
        except ImportError as e:
            self.logger.warning(f"Perception layer not available: {e}")
            
        try:
            from .layers.memory import MemoryLayer
            self.layers['memory'] = MemoryLayer(
                self.message_bus, 
                self.config_manager.get('memory', {})
            )
            self.logger.info("Memory layer initialized")
        except ImportError as e:
            self.logger.warning(f"Memory layer not available: {e}")
            
        try:
            from .layers.reasoning import ReasoningLayer
            self.layers['reasoning'] = ReasoningLayer(
                self.message_bus, 
                self.config_manager.get('reasoning', {})
            )
            self.logger.info("Reasoning layer initialized")
        except ImportError as e:
            self.logger.warning(f"Reasoning layer not available: {e}")
            
        try:
            from .layers.metacognition import MetacognitionLayer
            self.layers['metacognition'] = MetacognitionLayer(
                self.message_bus, 
                self.config_manager.get('metacognition', {})
            )
            self.logger.info("Metacognition layer initialized")
        except ImportError as e:
            self.logger.warning(f"Metacognition layer not available: {e}")
            
        try:
            from .layers.ethics import EthicsLayer
            self.layers['ethics'] = EthicsLayer(
                self.message_bus, 
                self.config_manager.get('ethics', {})
            )
            self.logger.info("Ethics layer initialized")
        except ImportError as e:
            self.logger.warning(f"Ethics layer not available: {e}")
            
        self.logger.info(f"Initialized {len(self.layers)} cognitive layers")
            
    def _load_dsl_config(self):
        """Загрузка DSL конфигурации"""
        dsl_config_path = self.config_manager.get('dsl.config_file', 'config/rules.aria')
        
        try:
            if os.path.exists(dsl_config_path):
                with open(dsl_config_path, 'r') as f:
                    dsl_code = f.read()
                    
                # Компиляция DSL
                lexer = Lexer(dsl_code)
                tokens = lexer.tokenize()
                
                parser = Parser(tokens)
                ast_nodes = parser.parse()
                
                self.dsl_compiler.compile(ast_nodes)
                
                self.logger.info(f"DSL configuration loaded and compiled ({len(self.dsl_compiler.compiled_rules)} rules)")
            else:
                self.logger.warning(f"DSL config file not found: {dsl_config_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading DSL config: {e}")
            
    def process_input(self, user_input: str) -> str:
        """Основная функция обработки пользовательского ввода"""
        try:
            # Создаем сообщение о пользовательском вводе
            input_message = Message(
                id=f"input_{hash(user_input)}",
                type=MessageType.USER_INPUT,
                source="user",
                target="system",
                payload={"text": user_input},
                timestamp=datetime.now()
            )
            
            # Публикуем сообщение
            self.message_bus.publish(input_message)
            
            # Обрабатываем сообщения
            self.message_bus.process_messages()
            
            # Запускаем когнитивный пайплайн
            response = self._cognitive_pipeline(user_input)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."
            
    def _cognitive_pipeline(self, user_input: str) -> str:
        """Основной когнитивный пайплайн"""
        context = {"user_input": user_input}
        
        # 1. Восприятие
        if 'perception' in self.layers:
            try:
                perception_result = self.layers['perception'].process(user_input)
                context.update(perception_result)
            except Exception as e:
                self.logger.warning(f"Perception layer error: {e}")
            
        # 2. Память
        if 'memory' in self.layers:
            try:
                memory_result = self.layers['memory'].process(context)
                context.update(memory_result)
            except Exception as e:
                self.logger.warning(f"Memory layer error: {e}")
            
        # 3. Рассуждение
        if 'reasoning' in self.layers:
            try:
                reasoning_result = self.layers['reasoning'].process(context)
                context.update(reasoning_result)
            except Exception as e:
                self.logger.warning(f"Reasoning layer error: {e}")
            
        # 4. Метакогниция
        if 'metacognition' in self.layers:
            try:
                meta_result = self.layers['metacognition'].process(context)
                context.update(meta_result)
            except Exception as e:
                self.logger.warning(f"Metacognition layer error: {e}")
            
        # 5. Этика
        if 'ethics' in self.layers:
            try:
                ethics_result = self.layers['ethics'].process(context)
                context.update(ethics_result)
            except Exception as e:
                self.logger.warning(f"Ethics layer error: {e}")
            
        # 6. Применение правил DSL
        try:
            self.dsl_interpreter.set_context(context)
            rule_results = self.dsl_interpreter.execute_rules()
        except Exception as e:
            self.logger.warning(f"DSL execution error: {e}")
            rule_results = []
        
        # Генерация ответа
        response = self._generate_response(context, rule_results, user_input)
        
        return response
        
    def _generate_response(self, context: Dict[str, Any], rule_results: List[Dict], user_input: str) -> str:
        """Генерация финального ответа"""
        # Если есть результаты DSL правил, используем их
        if rule_results:
            # Используем результат правила с наивысшей уверенностью
            best_result = max(rule_results, key=lambda x: x.get('confidence', 0))
            if best_result.get('confidence', 0) > 0.5:
                return str(best_result['result'])
        
        # Если в контексте есть готовый ответ от слоев
        if 'response' in context:
            return context['response']
            
        # Простые эвристики как fallback
        input_lower = user_input.lower()
        
        if any(greeting in input_lower for greeting in ['hello', 'hi', 'привет', 'здравствуй']):
            return "Привет! Как дела?"
        elif any(farewell in input_lower for farewell in ['bye', 'goodbye', 'пока', 'до свидания']):
            return "До свидания! Хорошего дня!"
        elif any(help_word in input_lower for help_word in ['help', 'помощь', 'помоги']):
            return "Я могу помочь вам с различными вопросами. Просто задайте свой вопрос!"
        elif '2+2' in input_lower:
            return "2+2=4"
        elif any(word in input_lower for word in ['кто ты', 'what are you']):
            return "Я TinyARIA - экспериментальная система искусственного интеллекта."
        else:
            return f"Я обработал ваш запрос: '{user_input}'. Система в разработке."
            
    def _handle_error(self, message: Message):
        """Обработка сообщений об ошибках"""
        self.logger.error(f"System error: {message.payload}")
        
    def _handle_metric(self, message: Message):
        """Обработка метрик"""
        self.logger.debug(f"Metric: {message.payload}")
        
    def shutdown(self):
        """Корректное завершение работы системы"""
        self.lifecycle_manager.shutdown()
        
    # Методы завершения работы компонентов
    def _shutdown_layers(self):
        for name, layer in self.layers.items():
            try:
                if hasattr(layer, 'shutdown'):
                    layer.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down layer {name}: {e}")
                
    def _shutdown_plugins(self):
        self.plugin_manager.shutdown_all()
        
    def _shutdown_message_bus(self):
        # Очистка очереди сообщений
        self.message_bus.message_queue.clear()