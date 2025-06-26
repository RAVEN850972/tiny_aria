#!/usr/bin/env python3
# quick_dsl_demo.py - Быстрая демонстрация DSL

import sys
import os

# Добавляем пути
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

def main():
    print("🤖 Quick DSL Demo")
    print("=" * 40)
    
    try:
        # Импортируем необходимые модули
        from src.dsl.lexer import Lexer
        from src.dsl.parser import Parser
        from src.dsl.compiler import DSLCompiler
        from src.dsl.interpreter import DSLInterpreter
        
        print("✅ All modules imported successfully")
        
        # DSL код с правилами
        dsl_code = '''
        rule "greeting" {
            if: "hello"
            then: "Hello! Nice to meet you!"
            confidence: 0.9
        }
        
        rule "help" {
            if: "help"
            then: "I'm here to help you!"
            confidence: 0.8
        }
        
        rule "goodbye" {
            if: "bye"
            then: "Goodbye! Have a great day!"
            confidence: 0.9
        }
        '''
        
        print("\n📝 Compiling DSL code...")
        
        # Компилируем DSL
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        print(f"   Generated {len(tokens)} tokens")
        
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        print(f"   Parsed {len(ast_nodes)} AST nodes")
        
        compiler = DSLCompiler()
        compiler.compile(ast_nodes)
        print(f"   Compiled {len(compiler.compiled_rules)} rules")
        
        # Создаем интерпретатор
        interpreter = DSLInterpreter(compiler)
        
        print("\n🎯 Testing rules...")
        
        # Тестируем различные входы
        test_cases = [
            "hello world",
            "I need help",
            "bye for now",
            "random input"
        ]
        
        for i, user_input in enumerate(test_cases, 1):
            print(f"\n{i}. Input: '{user_input}'")
            
            interpreter.set_context({"user_input": user_input})
            results = interpreter.execute_rules()
            
            if results:
                best = max(results, key=lambda x: x['confidence'])
                print(f"   Output: '{best['result']}'")
                print(f"   Rule: {best['rule']} (confidence: {best['confidence']})")
            else:
                print("   Output: No matching rules")
        
        print(f"\n📊 Statistics:")
        stats = interpreter.compiler.get_stats()
        print(f"   Total rules: {stats['rules_count']}")
        print(f"   Rule names: {', '.join(stats['rule_names'])}")
        
        print("\n🎉 DSL Demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)