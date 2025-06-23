# main.py
#!/usr/bin/env python3

import argparse
import sys
import os
from src.tiny_aria import TinyARIA

def main():
    parser = argparse.ArgumentParser(description='TinyARIA - Minimal ARIA Implementation')
    parser.add_argument(
        '--config', '-c', 
        default='config',
        help='Configuration directory path'
    )
    parser.add_argument(
        '--environment', '-e',
        default='development',
        help='Environment to run (development, production)'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--input', 
        help='Single input to process'
    )
    
    args = parser.parse_args()
    
    # Создаем директории если их нет
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Инициализируем TinyARIA
    aria = TinyARIA(args.config)
    
    if not aria.initialize(args.environment):
        print("Failed to initialize TinyARIA")
        sys.exit(1)
        
    try:
        if args.input:
            # Обработка одного запроса
            response = aria.process_input(args.input)
            print(response)
            
        elif args.interactive:
            # Интерактивный режим
            print("TinyARIA Interactive Mode")
            print("Type 'quit' or 'exit' to stop")
            print("-" * 40)
            
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                        
                    if user_input:
                        response = aria.process_input(user_input)
                        print(f"ARIA: {response}")
                        print()
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                    
        else:
            print("Use --interactive for interactive mode or --input for single query")
            
    finally:
        aria.shutdown()
        print("\nTinyARIA shutdown complete")

if __name__ == "__main__":
    main()