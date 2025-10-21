#!/usr/bin/env python3
"""
Скрипт для создания token.json для Google Calendar API
Требуется файл credentials.json из Google Cloud Console
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Укажите необходимые scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

# Пути к файлам (используем /app/data для volume)
DATA_DIR = '/app/data'
CREDENTIALS_FILE = os.path.join(DATA_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(DATA_DIR, 'token.json')

def create_token():
    """Создает token.json через OAuth 2.0 flow"""
    
    # Проверяем наличие credentials.json
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Файл {CREDENTIALS_FILE} не найден")
        print("\nКак получить credentials.json:")
        print("1. Перейдите в Google Cloud Console: https://console.cloud.google.com")
        print("2. Создайте проект или выберите существующий")
        print("3. Включите Google Calendar API")
        print("4. Создайте OAuth 2.0 Client ID (тип: Desktop app)")
        print("5. Скачайте JSON и сохраните как credentials.json")
        return
    
    # Удаляем старый токен, если есть
    if os.path.exists(TOKEN_FILE):
        print(f"Найден старый {TOKEN_FILE}. Удаление...")
        os.remove(TOKEN_FILE)
    
    print("Запуск авторизации...")
    print("Сейчас откроется браузер для входа в Google аккаунт\n")
    
    try:
        # Создаем OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            SCOPES
        )
        
        # Запускаем локальный сервер для получения токена
        # Используем порт 8080 для Docker
        creds = flow.run_local_server(
            port=8080,
            host='0.0.0.0'  # Слушаем на всех интерфейсах
        )
        
        # Сохраняем токен
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\nТокен успешно создан и сохранен в {TOKEN_FILE}")
        print(f"Полный путь: {os.path.abspath(TOKEN_FILE)}")
        
    except Exception as e:
        print(f"\n❌ Ошибка при создании токена: {e}")
        return

if __name__ == '__main__':
    create_token()
