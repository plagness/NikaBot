import logging
import os
from dotenv import load_dotenv
from plugin_manager import PluginManager
from ollama import OllamaAPI  # Импортируем OllamaAPI
from telegram_bot import ChatGPTTelegramBot
from ollama import OllamaAPI

    # Читаем .env файл
    load_dotenv()

    # Настраиваем логирование
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Проверяем наличие необходимых переменных окружения
    required_values = ['TELEGRAM_BOT_TOKEN', 'OLLAMA_API_URL', 'MODEL_NAME']
    missing_values = [value for value in required_values if os.environ.get(value) is None]
    if len(missing_values) > 0:
        logging.error(f'Отсутствуют следующие значения в вашем .env: {", ".join(missing_values)}')
        exit(1)

    # Настройка конфигурации Ollama
    ollama_config = {
        'api_url': os.environ.get('OLLAMA_API_URL'),
        'model_name': os.environ.get('MODEL_NAME'),
        'show_usage': os.environ.get('SHOW_USAGE', 'false').lower() == 'true',
        'stream': os.environ.get('STREAM', 'true').lower() == 'true',
        'max_history_size': int(os.environ.get('MAX_HISTORY_SIZE', 15)),
        'max_conversation_age_minutes': int(os.environ.get('MAX_CONVERSATION_AGE_MINUTES', 180)),
        'assistant_prompt': os.environ.get('ASSISTANT_PROMPT', 'You are a helpful assistant.'),
        'max_tokens': int(os.environ.get('MAX_TOKENS', 150)),
        'temperature': float(os.environ.get('TEMPERATURE', 1.0)),
        'bot_language': os.environ.get('BOT_LANGUAGE', 'en'),
    }

    telegram_config = {
        'token': os.environ['TELEGRAM_BOT_TOKEN'],
        'admin_user_ids': os.environ.get('ADMIN_USER_IDS', '-'),
        'allowed_user_ids': os.environ.get('ALLOWED_TELEGRAM_USER_IDS', '*'),
        'enable_quoting': os.environ.get('ENABLE_QUOTING', 'true').lower() == 'true',
        'enable_image_generation': os.environ.get('ENABLE_IMAGE_GENERATION', 'true').lower() == 'true',
        'enable_transcription': os.environ.get('ENABLE_TRANSCRIPTION', 'true').lower() == 'true',
        'enable_vision': os.environ.get('ENABLE_VISION', 'true').lower() == 'true',
        'enable_tts_generation': os.environ.get('ENABLE_TTS_GENERATION', 'true').lower() == 'true',
        'budget_period': os.environ.get('BUDGET_PERIOD', 'monthly').lower(),
        'user_budgets': os.environ.get('USER_BUDGETS', '*'),
        'guest_budget': float(os.environ.get('GUEST_BUDGET', '100.0')),
        'guest_budget': float(os.environ.get('GUEST_BUDGET', '100.0')),
        'proxy': os.environ.get('PROXY', None) or os.environ.get('TELEGRAM_PROXY', None),
        'voice_reply_transcript': os.environ.get('VOICE_REPLY_WITH_TRANSCRIPT_ONLY', 'false').lower() == 'true',
        'voice_reply_prompts': os.environ.get('VOICE_REPLY_PROMPTS', '').split(';'),
        'ignore_group_transcriptions': os.environ.get('IGNORE_GROUP_TRANSCRIPTIONS', 'true').lower() == 'true',
        'ignore_group_vision': os.environ.get('IGNORE_GROUP_VISION', 'true').lower() == 'true',
        'group_trigger_keyword': os.environ.get('GROUP_TRIGGER_KEYWORD', ''),
        'bot_language': os.environ.get('BOT_LANGUAGE', 'en'),
    }

    plugin_config = {
        'plugins': os.environ.get('PLUGINS', '').split(',')
    }

    # Настраиваем и запускаем бота
    plugin_manager = PluginManager(config=plugin_config)
    ollama_api = OllamaAPI(api_url=ollama_config['api_url'], model_name=ollama_config['model_name'])
    telegram_bot = ChatGPTTelegramBot(config=telegram_config, openai=ollama_api)
    telegram_bot.run()

if __name__ == '__main__':
    main()
    main()

    main()
# ... existing code...
# ... existing code...