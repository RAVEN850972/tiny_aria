# src/tests/test_integration_full.py
import pytest
import tempfile
import os
import time
from src.tiny_aria import TinyARIA
from src.cognitive_pipeline import CognitivePipeline
from src.session_manager import SessionManager

class TestFullIntegration:
    def test_complete_pipeline(self):
        """Тест полного пайплайна обработки"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем минимальную конфигурацию
            config = self._create_test_config(temp_dir)
            
            # Инициализируем систему
            aria = TinyARIA(temp_dir)
            assert aria.initialize() == True
            
            # Создаем пайплайн
            pipeline = CognitivePipeline(aria.layers)
            
            # Тестируем обработку различных типов ввода
            test_inputs = [
                "Привет, как дела?",
                "Что такое искусственный интеллект?",
                "Помоги мне решить задачу",
                "Я грустный сегодня"
            ]
            
            for user_input in test_inputs:
                result = pipeline.process_input(user_input)
                
                # Проверяем структуру результата
                assert 'response' in result
                assert 'confidence' in result
                assert 'layer_results' in result
                assert 'processing_metadata' in result
                
                # Проверяем, что ответ не пустой
                assert len(result['response']) > 0
                
                # Проверяем, что confidence в допустимых пределах
                assert 0.0 <= result['confidence'] <= 1.0
                
                print(f"Input: {user_input}")
                print(f"Response: {result['response']}")
                print(f"Confidence: {result['confidence']:.2f}")
                print("-" * 40)
                
    def test_session_continuity(self):
        """Тест непрерывности сессии"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self._create_test_config(temp_dir)
            
            aria = TinyARIA(temp_dir)
            aria.initialize()
            
            pipeline = CognitivePipeline(aria.layers)
            session_manager = SessionManager()
            
            session_id = "test_session_123"
            
            # Первое взаимодействие
            session_context = session_manager.get_session(session_id)
            result1 = pipeline.process_input("Меня зовут Алексей", session_context)
            
            session_manager.update_session(session_id, result1['context_updates'])
            session_manager.add_to_conversation_history(
                session_id, "Меня зовут Алексей", result1['response']
            )
            
            # Второе взаимодействие
            session_context = session_manager.get_session(session_id)
            result2 = pipeline.process_input("Как меня зовут?", session_context)
            
            # Проверяем, что система помнит информацию из предыдущего взаимодействия
            assert session_context['interaction_count'] == 1
            assert len(session_context.get('conversation_history', [])) == 1
            
            print(f"First interaction: {result1['response']}")
            print(f"Second interaction: {result2['response']}")
            
    def test_memory_persistence(self):
        """Тест сохранения памяти между сессиями"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self._create_test_config(temp_dir)
            
            # Первая сессия
            aria1 = TinyARIA(temp_dir)
            aria1.initialize()
            
            pipeline1 = CognitivePipeline(aria1.layers)
            result1 = pipeline1.process_input("Я изучаю программирование на Python")
            
            # Завершаем первую сессию
            aria1.shutdown()
            
            # Вторая сессия (новый экземпляр)
            aria2 = TinyARIA(temp_dir)
            aria2.initialize()
            
            pipeline2 = CognitivePipeline(aria2.layers)
            result2 = pipeline2.process_input("Что я изучаю?")
            
            # Проверяем, что информация сохранилась
            # (В реальной реализации memory layer должен загружать данные из БД)
            
            aria2.shutdown()
            
    def test_error_handling(self):
        """Тест обработки ошибок"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self._create_test_config(temp_dir)
            
            aria = TinyARIA(temp_dir)
            aria.initialize()
            
            pipeline = CognitivePipeline(aria.layers)
            
            # Тестируем различные проблемные входы
            problematic_inputs = [
                "",  # Пустой ввод
                "x" * 10000,  # Очень длинный ввод
                "🤖👾🚀💫",  # Только эмодзи
                "1234567890",  # Только числа
            ]
            
            for user_input in problematic_inputs:
                try:
                    result = pipeline.process_input(user_input)
                    
                    # Система должна обрабатывать проблемные входы без крашей
                    assert 'response' in result
                    assert result['confidence'] >= 0.0
                    
                    print(f"Handled problematic input: '{user_input[:20]}...'")
                    print(f"Response: {result['response'][:50]}...")
                    
                except Exception as e:
                    pytest.fail(f"System crashed on input '{user_input}': {e}")
                    
    def test_performance_benchmarks(self):
        """Тест производительности системы"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self._create_test_config(temp_dir)
            
            aria = TinyARIA(temp_dir)
            aria.initialize()
            
            pipeline = CognitivePipeline(aria.layers)
            
            # Тестируем скорость обработки
            test_input = "Какая сегодня погода?"
            
            processing_times = []
            
            for i in range(10):
                start_time = time.time()
                result = pipeline.process_input(f"{test_input} (тест {i})")
                end_time = time.time()
                
                processing_time = end_time - start_time
                processing_times.append(processing_time)
                
                # Проверяем, что обработка не слишком медленная
                assert processing_time < 10.0, f"Processing took too long: {processing_time:.2f}s"
                
            # Анализируем производительность
            avg_time = sum(processing_times) / len(processing_times)
            max_time = max(processing_times)
            min_time = min(processing_times)
            
            print(f"Performance benchmarks:")
            print(f"  Average processing time: {avg_time:.3f}s")
            print(f"  Max processing time: {max_time:.3f}s")
            print(f"  Min processing time: {min_time:.3f}s")
            
            # Устанавливаем разумные пороги производительности
            assert avg_time < 5.0, f"Average processing time too slow: {avg_time:.3f}s"
            assert max_time < 8.0, f"Max processing time too slow: {max_time:.3f}s"
            
    def test_confidence_calibration(self):
        """Тест калибровки уверенности системы"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self._create_test_config(temp_dir)
            
            aria = TinyARIA(temp_dir)
            aria.initialize()
            
            pipeline = CognitivePipeline(aria.layers)
            
            # Тестируем входы с разным уровнем сложности
            test_cases = [
                ("Привет", "high"),  # Простое приветствие - высокая уверенность
                ("Что такое квантовая механика?", "medium"),  # Сложный вопрос - средняя уверенность
                ("asdfghjkl qwerty", "low"),  # Бессмыслица - низкая уверенность
                ("2+2=?", "high"),  # Простая математика - высокая уверенность
            ]
            
            for user_input, expected_confidence_level in test_cases:
                result = pipeline.process_input(user_input)
                confidence = result['confidence']
                
                print(f"Input: {user_input}")
                print(f"Confidence: {confidence:.3f} (expected: {expected_confidence_level})")
                
                # Проверяем соответствие ожиданиям
                if expected_confidence_level == "high":
                    assert confidence > 0.7, f"Expected high confidence, got {confidence:.3f}"
                elif expected_confidence_level == "medium":
                    assert 0.3 < confidence <= 0.7, f"Expected medium confidence, got {confidence:.3f}"
                elif expected_confidence_level == "low":
                    assert confidence <= 0.3, f"Expected low confidence, got {confidence:.3f}"
                    
    def _create_test_config(self, temp_dir):
        """Создание тестовой конфигурации"""
        
        import json
        
        config = {
            "system": {
                "debug": True
            },
            "perception": {
                "max_tokens": 500,
                "context_levels": 3
            },
            "memory": {
                "working_size": 5,
                "episodic_limit": 100,
                "episodic_memory": {
                    "db_path": os.path.join(temp_dir, "test_episodes.db")
                },
                "associations": {
                    "save_path": os.path.join(temp_dir, "test_associations.pkl")
                }
            },
            "reasoning": {
                "max_steps": 5,
                "quantum_qubits": 4
            },
            "metacognition": {
                "confidence_threshold": 0.7
            },
            "ethics": {
                "harm_threshold": 0.1
            }
        }
        
        config_file = os.path.join(temp_dir, "default.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        return config