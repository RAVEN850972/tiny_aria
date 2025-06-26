# src/cognitive_pipeline.py
from typing import Dict, Any, List
import logging
import time
from dataclasses import dataclass

@dataclass
class ProcessingResult:
    layer_name: str
    success: bool
    result: Dict[str, Any]
    processing_time: float
    confidence: float
    errors: List[str]

class CognitivePipeline:
    """Координатор обработки через все когнитивные слои"""
    
    def __init__(self, layers: Dict[str, Any]):
        self.layers = layers
        self.logger = logging.getLogger(__name__)
        
        # Определяем порядок обработки
        self.processing_order = [
            'perception',
            'memory',
            'reasoning',
            'metacognition', 
            'ethics'
        ]
        
    def process_input(self, user_input: str, session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Полная обработка входа через все слои"""
        
        if session_context is None:
            session_context = {}
            
        pipeline_start = time.time()
        
        # Контекст, который передается между слоями
        processing_context = {
            'user_input': user_input,
            'session_context': session_context,
            'timestamp': time.time(),
            'pipeline_id': f"pipeline_{int(time.time())}"
        }
        
        # Результаты обработки по слоям
        layer_results = {}
        processing_metadata = []
        
        # Последовательная обработка через все слои
        for layer_name in self.processing_order:
            if layer_name in self.layers:
                layer_result = self._process_layer(
                    layer_name, 
                    self.layers[layer_name], 
                    processing_context
                )
                
                layer_results[layer_name] = layer_result.result
                processing_metadata.append(layer_result)
                
                # Обновляем контекст результатами слоя
                if layer_result.success:
                    processing_context[f'{layer_name}_result'] = layer_result.result
                else:
                    self.logger.warning(f"Layer {layer_name} failed: {layer_result.errors}")
                    
        # Финальная обработка и генерация ответа
        final_result = self._synthesize_results(
            user_input, 
            processing_context, 
            layer_results
        )
        
        pipeline_time = time.time() - pipeline_start
        
        return {
            'response': final_result['response'],
            'confidence': final_result['confidence'],
            'layer_results': layer_results,
            'processing_metadata': {
                'pipeline_time': pipeline_time,
                'layers_processed': len(processing_metadata),
                'layer_details': processing_metadata,
                'pipeline_id': processing_context['pipeline_id']
            },
            'context_updates': final_result.get('context_updates', {})
        }
        
    def _process_layer(self, layer_name: str, layer_instance, context: Dict[str, Any]) -> ProcessingResult:
        """Обработка одного слоя"""
        
        start_time = time.time()
        errors = []
        
        try:
            # Подготавливаем входные данные для слоя
            layer_input = self._prepare_layer_input(layer_name, context)
            
            # Выполняем обработку
            result = layer_instance.process(layer_input)
            
            # Вычисляем confidence
            confidence = self._extract_confidence(result, layer_name)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                layer_name=layer_name,
                success=True,
                result=result,
                processing_time=processing_time,
                confidence=confidence,
                errors=errors
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error in {layer_name}: {str(e)}"
            errors.append(error_msg)
            self.logger.error(error_msg)
            
            return ProcessingResult(
                layer_name=layer_name,
                success=False,
                result={},
                processing_time=processing_time,
                confidence=0.0,
                errors=errors
            )
            
    def _prepare_layer_input(self, layer_name: str, context: Dict[str, Any]):
        """Подготовка входных данных для конкретного слоя"""
        
        if layer_name == 'perception':
            # Для слоя восприятия нужен только пользовательский ввод
            return context['user_input']
            
        elif layer_name == 'memory':
            # Для памяти нужен полный контекст
            return context
            
        elif layer_name == 'reasoning':
            # Для рассуждений нужны результаты восприятия и памяти
            return {
                'user_input': context['user_input'],
                'perception_result': context.get('perception_result', {}),
                'memory_result': context.get('memory_result', {}),
                'session_context': context.get('session_context', {})
            }
            
        elif layer_name == 'metacognition':
            # Для метакогниции нужны результаты всех предыдущих слоев
            return {
                'user_input': context['user_input'],
                'perception_result': context.get('perception_result', {}),
                'memory_result': context.get('memory_result', {}),
                'reasoning_result': context.get('reasoning_result', {}),
                'processing_history': context.get('processing_history', [])
            }
            
        elif layer_name == 'ethics':
            # Для этики нужны все результаты для оценки
            return context
            
        else:
            # По умолчанию передаем весь контекст
            return context
            
    def _extract_confidence(self, result: Dict[str, Any], layer_name: str) -> float:
        """Извлечение уверенности из результата слоя"""
        
        confidence_keys = [
            f'{layer_name}_confidence',
            'confidence',
            'overall_confidence',
            'certainty'
        ]
        
        for key in confidence_keys:
            if key in result:
                return float(result[key])
                
        # Если confidence не найден, вычисляем на основе наличия ошибок
        if 'error' in result:
            return 0.0
        else:
            return 0.7  # Средняя уверенность по умолчанию
            
    def _synthesize_results(self, user_input: str, context: Dict[str, Any], 
                           layer_results: Dict[str, Any]) -> Dict[str, Any]:
        """Синтез финального результата из всех слоев"""
        
        # Извлекаем ключевую информацию из каждого слоя
        synthesis_data = self._extract_synthesis_data(layer_results)
        
        # Генерируем ответ
        response = self._generate_response(user_input, synthesis_data, context)
        
        # Вычисляем общую уверенность
        overall_confidence = self._calculate_overall_confidence(layer_results)
        
        # Подготавливаем обновления контекста для сессии
        context_updates = self._prepare_context_updates(synthesis_data, layer_results)
        
        return {
            'response': response,
            'confidence': overall_confidence,
            'synthesis_data': synthesis_data,
            'context_updates': context_updates
        }
        
    def _extract_synthesis_data(self, layer_results: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечение ключевых данных для синтеза"""
        
        synthesis = {
            'concepts': [],
            'intent': 'unknown',
            'emotional_tone': 'neutral',
            'relevant_memories': [],
            'reasoning_steps': [],
            'ethical_assessment': {},
            'confidence_levels': {}
        }
        
        # Данные из восприятия
        if 'perception' in layer_results:
            perception = layer_results['perception']
            
            if 'semantic_map' in perception:
                synthesis['concepts'] = [
                    concept.name for concept in perception['semantic_map'].concepts
                ]
                
            if 'context_analysis' in perception:
                context_analysis = perception['context_analysis']
                synthesis['intent'] = context_analysis.primary_intent
                synthesis['emotional_tone'] = context_analysis.emotional_tone
                
            synthesis['confidence_levels']['perception'] = perception.get('perception_confidence', 0.5)
            
        # Данные из памяти
        if 'memory' in layer_results:
            memory = layer_results['memory']
            synthesis['relevant_memories'] = memory.get('relevant_memories', [])
            synthesis['confidence_levels']['memory'] = 0.8  # Память обычно надежна
            
        # Данные из рассуждений
        if 'reasoning' in layer_results:
            reasoning = layer_results['reasoning']
            synthesis['reasoning_steps'] = reasoning.get('reasoning_chain', [])
            synthesis['confidence_levels']['reasoning'] = reasoning.get('reasoning_confidence', 0.5)
            
        # Данные из этики
        if 'ethics' in layer_results:
            ethics = layer_results['ethics']
            synthesis['ethical_assessment'] = ethics.get('ethical_evaluation', {})
            synthesis['confidence_levels']['ethics'] = ethics.get('ethical_confidence', 0.5)
            
        return synthesis
        
    def _generate_response(self, user_input: str, synthesis_data: Dict[str, Any], 
                          context: Dict[str, Any]) -> str:
        """Генерация финального ответа"""
        
        intent = synthesis_data.get('intent', 'unknown')
        concepts = synthesis_data.get('concepts', [])
        memories = synthesis_data.get('relevant_memories', [])
        ethical_assessment = synthesis_data.get('ethical_assessment', {})
        
        # Проверяем этические ограничения
        if ethical_assessment.get('blocked', False):
            return ethical_assessment.get('explanation', 
                'Извините, я не могу ответить на этот запрос по этическим соображениям.')
        
        # Генерируем ответ на основе намерения
        if intent == 'greeting':
            return self._generate_greeting_response(synthesis_data)
            
        elif intent == 'question':
            return self._generate_question_response(user_input, synthesis_data, memories)
            
        elif intent == 'command':
            return self._generate_command_response(user_input, synthesis_data)
            
        elif intent == 'emotional_expression':
            return self._generate_emotional_response(synthesis_data)
            
        else:
            return self._generate_default_response(user_input, synthesis_data)
            
    def _generate_greeting_response(self, synthesis_data: Dict[str, Any]) -> str:
        """Генерация ответа на приветствие"""
        
        emotional_tone = synthesis_data.get('emotional_tone', 'neutral')
        
        if emotional_tone == 'positive' or emotional_tone == 'very_positive':
            return "Привет! Я рад вас видеть! Как дела?"
        elif emotional_tone == 'negative':
            return "Здравствуйте. Как дела? Могу ли я чем-то помочь?"
        else:
            return "Здравствуйте! Как поживаете?"
            
    def _generate_question_response(self, user_input: str, synthesis_data: Dict[str, Any], 
                                   memories: List[Dict]) -> str:
        """Генерация ответа на вопрос"""
        
        # Ищем релевантную информацию в памяти
        relevant_info = []
        
        for memory in memories[:3]:  # Берем топ 3 воспоминания
            if memory['source'] == 'episodic_memory':
                content = memory['content']['content']
                if 'response' in content:
                    relevant_info.append(content['response'])
                    
        if relevant_info:
            # Используем информацию из памяти
            base_response = f"На основе того, что я помню: {relevant_info[0]}"
        else:
            # Генерируем новый ответ
            concepts = synthesis_data.get('concepts', [])
            if concepts:
                base_response = f"Я понимаю, что вы спрашиваете о {', '.join(concepts[:3])}. "
            else:
                base_response = "Это интересный вопрос. "
                
        # Добавляем метакогнитивную информацию
        confidence = synthesis_data.get('confidence_levels', {}).get('reasoning', 0.5)
        
        if confidence < 0.6:
            base_response += " Хотя я не совсем уверен в своем ответе."
        elif confidence > 0.8:
            base_response += " Я довольно уверен в этом ответе."
            
        return base_response
        
    def _generate_command_response(self, user_input: str, synthesis_data: Dict[str, Any]) -> str:
        """Генерация ответа на команду"""
        
        concepts = synthesis_data.get('concepts', [])
        
        if any(concept in ['help', 'помощь'] for concept in concepts):
            return ("Я могу помочь вам с различными вопросами и задачами. "
                   "Просто опишите, что вам нужно, и я постараюсь помочь.")
        else:
            return f"Я понял, что вы хотите {user_input.lower()}. Постараюсь помочь."
            
    def _generate_emotional_response(self, synthesis_data: Dict[str, Any]) -> str:
        """Генерация ответа на эмоциональное выражение"""
        
        emotional_tone = synthesis_data.get('emotional_tone', 'neutral')
        
        if emotional_tone in ['positive', 'very_positive']:
            return "Я рад, что у вас хорошее настроение! Это замечательно."
        elif emotional_tone in ['negative', 'very_negative']:
            return "Я понимаю, что вы расстроены. Хотите поговорить об этом?"
        else:
            return "Я понимаю ваши чувства. Спасибо, что поделились со мной."
            
    def _generate_default_response(self, user_input: str, synthesis_data: Dict[str, Any]) -> str:
        """Генерация ответа по умолчанию"""
        
        concepts = synthesis_data.get('concepts', [])
        
        if concepts:
            return (f"Я обработал ваше сообщение и выделил следующие ключевые темы: "
                   f"{', '.join(concepts[:5])}. Можете ли вы уточнить, что именно вас интересует?")
        else:
            return ("Я получил ваше сообщение, но мне нужно больше информации, "
                   "чтобы дать полезный ответ. Не могли бы вы уточнить?")
            
    def _calculate_overall_confidence(self, layer_results: Dict[str, Any]) -> float:
        """Расчет общей уверенности системы"""
        
        confidences = []
        
        for layer_name, result in layer_results.items():
            if isinstance(result, dict) and not result.get('error'):
                # Извлекаем confidence для каждого слоя
                layer_confidence = self._extract_confidence(result, layer_name)
                confidences.append(layer_confidence)
                
        if not confidences:
            return 0.0
            
        # Используем среднее гармоническое для консервативной оценки
        harmonic_mean = len(confidences) / sum(1/c for c in confidences if c > 0)
        
        return min(harmonic_mean, 1.0)
        
    def _prepare_context_updates(self, synthesis_data: Dict[str, Any], 
                                layer_results: Dict[str, Any]) -> Dict[str, Any]:
        """Подготовка обновлений контекста сессии"""
        
        updates = {
            'last_concepts': synthesis_data.get('concepts', []),
            'last_intent': synthesis_data.get('intent', 'unknown'),
            'last_emotional_tone': synthesis_data.get('emotional_tone', 'neutral'),
            'interaction_count': 1,  # Будет увеличиваться в session manager
            'timestamp': time.time()
        }
        
        # Добавляем информацию о памяти
        if 'memory' in layer_results:
            memory_result = layer_results['memory']
            updates['last_episode_id'] = memory_result.get('current_episode_id')
            updates['activated_concepts'] = list(memory_result.get('activated_concepts', {}).keys())
            
        return updates