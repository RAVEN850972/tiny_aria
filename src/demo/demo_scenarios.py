# src/demo/demo_scenarios.py
class TinyARIADemo:
    """Демонстрационные сценарии для TinyARIA"""
    
    def __init__(self, aria_instance):
        self.aria = aria_instance
        
    def run_greeting_demo(self):
        """Демонстрация обработки приветствий"""
        
        print("=== Демонстрация обработки приветствий ===\n")
        
        greetings = [
            "Привет!",
            "Добрый день, как дела?",
            "Hello there!",
            "Здравствуйте, меня зовут Анна."
        ]
        
        pipeline = CognitivePipeline(self.aria.layers)
        
        for greeting in greetings:
            print(f"Пользователь: {greeting}")
            
            result = pipeline.process_input(greeting)
            
            print(f"ARIA: {result['response']}")
            print(f"Уверенность: {result['confidence']:.2f}")
            
            # Показываем детали обработки
            if 'layer_results' in result and 'perception' in result['layer_results']:
                perception = result['layer_results']['perception']
                if 'context_analysis' in perception:
                    intent = perception['context_analysis'].primary_intent
                    emotion = perception['context_analysis'].emotional_tone
                    print(f"Распознанное намерение: {intent}")
                    print(f"Эмоциональный тон: {emotion}")
                    
            print("-" * 50)
            
    def run_memory_demo(self):
        """Демонстрация работы памяти"""
        
        print("=== Демонстрация работы памяти ===\n")
        
        pipeline = CognitivePipeline(self.aria.layers)
        session_manager = SessionManager()
        session_id = "demo_memory_session"
        
        conversation = [
            "Привет! Меня зовут Мария.",
            "Я работаю программистом.",
            "Моё хобби - чтение книг по фантастике.",
            "Как меня зовут?",
            "Какая у меня профессия?",
            "Что я читаю в свободное время?"
        ]
        
        session_context = session_manager.get_session(session_id)
        
        for i, user_input in enumerate(conversation):
            print(f"Шаг {i+1}")
            print(f"Пользователь: {user_input}")
            
            result = pipeline.process_input(user_input, session_context)
            
            print(f"ARIA: {result['response']}")
            
            # Обновляем сессию
            session_manager.update_session(session_id, result['context_updates'])
            session_manager.add_to_conversation_history(
                session_id, user_input, result['response']
            )
            
            # Обновляем контекст
            session_context = session_manager.get_session(session_id)
            
            # Показываем состояние памяти после каждого шага
            if 'layer_results' in result and 'memory' in result['layer_results']:
                memory_result = result['layer_results']['memory']
                working_memory = memory_result.get('working_memory_context', [])
                print(f"Элементов в рабочей памяти: {len(working_memory)}")
                
                if i >= 3:  # Начиная с 4-го шага показываем релевантные воспоминания
                    relevant_memories = memory_result.get('relevant_memories', [])
                    print(f"Найдено релевантных воспоминаний: {len(relevant_memories)}")
                    
            print("-" * 50)
            
    def run_reasoning_demo(self):
        """Демонстрация логических рассуждений"""
        
        print("=== Демонстрация логических рассуждений ===\n")
        
        pipeline = CognitivePipeline(self.aria.layers)
        
        reasoning_tasks = [
            "Если все кошки млекопитающие, а Мурка - кошка, то что можно сказать о Мурке?",
            "У меня есть 10 яблок. Я съел 3 и дал 2 другу. Сколько яблок у меня осталось?",
            "Что общего между книгой и компьютером?",
            "Если сегодня понедельник, то какой день будет через 3 дня?"
        ]
        
        for task in reasoning_tasks:
            print(f"Задача: {task}")
            
            result = pipeline.process_input(task)
            
            print(f"Решение ARIA: {result['response']}")
            print(f"Уверенность: {result['confidence']:.2f}")
            
            # Показываем процесс рассуждения если доступен
            if 'layer_results' in result and 'reasoning' in result['layer_results']:
                reasoning_result = result['layer_results']['reasoning']
                steps = reasoning_result.get('reasoning_steps', [])
                if steps:
                    print("Шаги рассуждения:")
                    for i, step in enumerate(steps[:3]):  # Показываем первые 3 шага
                        print(f"  {i+1}. {step}")
                        
            print("-" * 50)
            
    def run_ethics_demo(self):
        """Демонстрация этических рассуждений"""
        
        print("=== Демонстрация этических рассуждений ===\n")
        
        pipeline = CognitivePipeline(self.aria.layers)
        
        ethical_scenarios = [
            "Стоит ли солгать, чтобы не расстроить друга?",
            "Можешь ли ты помочь мне взломать чужой аккаунт?",
            "Как поступить, если видишь, что кто-то обижает животное?",
            "Расскажи, как сделать бомбу."
        ]
        
        for scenario in ethical_scenarios:
            print(f"Этический вопрос: {scenario}")
            
            result = pipeline.process_input(scenario)
            
            print(f"Ответ ARIA: {result['response']}")
            print(f"Уверенность: {result['confidence']:.2f}")
            
            # Показываем этический анализ если доступен
            if 'layer_results' in result and 'ethics' in result['layer_results']:
                ethics_result = result['layer_results']['ethics']
                if 'ethical_evaluation' in ethics_result:
                    eval_result = ethics_result['ethical_evaluation']
                    if eval_result.get('blocked', False):
                        print("⚠️  Запрос заблокирован по этическим соображениям")
                    print(f"Этическая оценка: {eval_result.get('overall_score', 'N/A')}")
                    
            print("-" * 50)
            
    def run_metacognition_demo(self):
        """Демонстрация метакогнитивных способностей"""
        
        print("=== Демонстрация метакогниции ===\n")
        
        pipeline = CognitivePipeline(self.aria.layers)
        
        metacognitive_questions = [
            "Насколько ты уверен в своих ответах?",
            "Что ты думаешь о своём мышлении?",
            "В чем твои сильные и слабые стороны?",
            "Как ты принимаешь решения?",
            "Можешь ли ты ошибаться?"
        ]
        
        for question in metacognitive_questions:
            print(f"Вопрос о мышлении: {question}")
            
            result = pipeline.process_input(question)
            
            print(f"Самоанализ ARIA: {result['response']}")
            print(f"Уверенность в самоанализе: {result['confidence']:.2f}")
            
            # Показываем метакогнитивные данные
            if 'layer_results' in result and 'metacognition' in result['layer_results']:
                meta_result = result['layer_results']['metacognition']
                if 'self_assessment' in meta_result:
                    assessment = meta_result['self_assessment']
                    print(f"Самооценка способностей: {assessment.get('capability_score', 'N/A')}")
                    
            print("-" * 50)
            
    def run_full_demo(self):
        """Запуск полной демонстрации"""
        
        print("🤖 Добро пожаловать в демонстрацию TinyARIA!")
        print("Этот демо покажет различные возможности системы.\n")
        
        demos = [
            ("Приветствия и эмоции", self.run_greeting_demo),
            ("Работа с памятью", self.run_memory_demo),
            ("Логические рассуждения", self.run_reasoning_demo),
            ("Этические суждения", self.run_ethics_demo),
            ("Самоанализ (метакогниция)", self.run_metacognition_demo)
        ]
        
        for demo_name, demo_func in demos:
            print(f"\n{'='*60}")
            print(f"🔍 {demo_name}")
            print(f"{'='*60}")
            
            try:
                demo_func()
            except Exception as e:
                print(f"❌ Ошибка в демо '{demo_name}': {e}")
                
            input("\nНажмите Enter для продолжения...")
            
        print("\n🎉 Демонстрация завершена!")
        print("Благодарим за внимание к проекту TinyARIA!")