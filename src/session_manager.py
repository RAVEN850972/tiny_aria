# src/session_manager.py
from typing import Dict, Any, Optional
import time
import json
import os

class SessionManager:
    """Управление пользовательскими сессиями"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = self.config.get('session_timeout', 3600)  # 1 час
        self.save_path = self.config.get('sessions_save_path', 'data/sessions.json')
        
        self._load_sessions()
        
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Получение или создание сессии"""
        
        current_time = time.time()
        
        # Проверяем, существует ли сессия и не истекла ли она
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            if current_time - session.get('last_activity', 0) < self.session_timeout:
                # Обновляем время последней активности
                session['last_activity'] = current_time
                return session
            else:
                # Сессия истекла, удаляем её
                del self.sessions[session_id]
                
        # Создаем новую сессию
        new_session = {
            'session_id': session_id,
            'created_at': current_time,
            'last_activity': current_time,
            'interaction_count': 0,
            'user_preferences': {},
            'conversation_history': [],
            'context': {
                'last_concepts': [],
                'last_intent': 'unknown',
                'last_emotional_tone': 'neutral',
                'activated_concepts': [],
                'user_profile': {}
            }
        }
        
        self.sessions[session_id] = new_session
        return new_session
        
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Обновление сессии"""
        
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session['last_activity'] = time.time()
            session['interaction_count'] += 1
            
            # Обновляем контекст
            if 'context' not in session:
                session['context'] = {}
                
            for key, value in updates.items():
                session['context'][key] = value
                
            # Ограничиваем историю разговора
            max_history = self.config.get('max_conversation_history', 50)
            if len(session.get('conversation_history', [])) > max_history:
                session['conversation_history'] = session['conversation_history'][-max_history:]
                
    def add_to_conversation_history(self, session_id: str, user_input: str, 
                                   ai_response: str, metadata: Dict[str, Any] = None):
        """Добавление записи в историю разговора"""
        
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            if 'conversation_history' not in session:
                session['conversation_history'] = []
                
            conversation_entry = {
                'timestamp': time.time(),
                'user_input': user_input,
                'ai_response': ai_response,
                'metadata': metadata or {}
            }
            
            session['conversation_history'].append(conversation_entry)
            
    def cleanup_expired_sessions(self):
        """Удаление истекших сессий"""
        
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.get('last_activity', 0) > self.session_timeout:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            del self.sessions[session_id]
            
        if expired_sessions:
            self._save_sessions()
            
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Получение статистики сессии"""
        
        if session_id not in self.sessions:
            return {}
            
        session = self.sessions[session_id]
        current_time = time.time()
        
        return {
            'session_duration': current_time - session.get('created_at', current_time),
            'interaction_count': session.get('interaction_count', 0),
            'last_activity': session.get('last_activity', 0),
            'conversation_length': len(session.get('conversation_history', [])),
            'context_size': len(session.get('context', {}))
        }
        
    def _save_sessions(self):
        """Сохранение сессий"""
        
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        
        # Фильтруем активные сессии
        active_sessions = {}
        current_time = time.time()
        
        for session_id, session in self.sessions.items():
            if current_time - session.get('last_activity', 0) < self.session_timeout:
                active_sessions[session_id] = session
                
        try:
            with open(self.save_path, 'w') as f:
                json.dump(active_sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
            
    def _load_sessions(self):
        """Загрузка сессий"""
        
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r') as f:
                    saved_sessions = json.load(f)
                    
                # Фильтруем не истекшие сессии
                current_time = time.time()
                
                for session_id, session in saved_sessions.items():
                    if current_time - session.get('last_activity', 0) < self.session_timeout:
                        self.sessions[session_id] = session
                        
            except Exception as e:
                print(f"Error loading sessions: {e}")

# Обновление main.py для использования пайплайна
def update_main_with_pipeline():
    """Обновление главного файла для использования когнитивного пайплайна"""
    
    main_code = '''
# main.py - обновленная версия с пайплайном

#!/usr/bin/env python3

import argparse
import sys
import os
import uuid
from src.tiny_aria import TinyARIA
from src.cognitive_pipeline import CognitivePipeline
from src.session_manager import SessionManager

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
    parser.add_argument(
        '--session-id',
        help='Session ID for conversation continuity'
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
        
    # Создаем когнитивный пайплайн
    pipeline = CognitivePipeline(aria.layers)
    
    # Инициализируем менеджер сессий
    session_manager = SessionManager()
    
    # Генерируем ID сессии если не указан
    session_id = args.session_id or str(uuid.uuid4())
    
    try:
        if args.input:
            # Обработка одного запроса
            session_context = session_manager.get_session(session_id)
            
            result = pipeline.process_input(args.input, session_context)
            
            print(f"ARIA: {result['response']}")
            print(f"Confidence: {result['confidence']:.2f}")
            
            # Обновляем сессию
            session_manager.update_session(session_id, result['context_updates'])
            session_manager.add_to_conversation_history(
                session_id, args.input, result['response'], 
                result['processing_metadata']
            )
            
        elif args.interactive:
            # Интерактивный режим
            print("TinyARIA Interactive Mode")
            print(f"Session ID: {session_id}")
            print("Type 'quit' or 'exit' to stop")
            print("Type 'stats' to see session statistics")
            print("Type 'history' to see conversation history")
            print("-" * 50)
            
            session_context = session_manager.get_session(session_id)
            
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                        
                    if user_input.lower() == 'stats':
                        stats = session_manager.get_session_stats(session_id)
                        print(f"Session Statistics:")
                        print(f"  Duration: {stats.get('session_duration', 0):.0f} seconds")
                        print(f"  Interactions: {stats.get('interaction_count', 0)}")
                        print(f"  Conversation length: {stats.get('conversation_length', 0)}")
                        continue
                        
                    if user_input.lower() == 'history':
                        history = session_context.get('conversation_history', [])
                        print(f"Conversation History ({len(history)} entries):")
                        for i, entry in enumerate(history[-5:]):  # Последние 5
                            print(f"  {i+1}. You: {entry['user_input'][:50]}...")
                            print(f"     ARIA: {entry['ai_response'][:50]}...")
                        continue
                        
                    if user_input:
                        # Обрабатываем ввод через пайплайн
                        result = pipeline.process_input(user_input, session_context)
                        
                        print(f"ARIA: {result['response']}")
                        
                        # Показываем confidence если он низкий
                        if result['confidence'] < 0.6:
                            print(f"(Confidence: {result['confidence']:.2f})")
                        
                        # Обновляем сессию
                        session_manager.update_session(session_id, result['context_updates'])
                        session_manager.add_to_conversation_history(
                            session_id, user_input, result['response'],
                            result['processing_metadata']
                        )
                        
                        # Обновляем контекст для следующей итерации
                        session_context = session_manager.get_session(session_id)
                        
                        print()
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    
        else:
            print("Use --interactive for interactive mode or --input for single query")
            
    finally:
        # Сохраняем сессии и завершаем работу
        session_manager._save_sessions()
        aria.shutdown()
        print("\\nTinyARIA shutdown complete")

if __name__ == "__main__":
    main()
    '''
    
    with open('main.py', 'w') as f:
        f.write(main_code)