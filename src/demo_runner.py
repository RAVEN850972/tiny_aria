# src/demo_runner.py
#!/usr/bin/env python3

def main():
    """Запуск демонстрации TinyARIA"""
    
    import sys
    import os
    
    # Добавляем путь к модулям
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.tiny_aria import TinyARIA
    from src.demo.demo_scenarios import TinyARIADemo
    
    print("Инициализация TinyARIA для демонстрации...")
    
    # Создаем директории
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Инициализируем TinyARIA
    aria = TinyARIA('config')
    
    if not aria.initialize('development'):
        print("❌ Не удалось инициализировать TinyARIA")
        sys.exit(1)
        
    print("✅ TinyARIA инициализирована успешно!\n")
    
    # Запускаем демонстрацию
    demo = TinyARIADemo(aria)
    
    try:
        demo.run_full_demo()
    finally:
        aria.shutdown()

if __name__ == "__main__":
    main()