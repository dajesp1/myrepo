from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import openai
import os


app = FastAPI()

# --- Настройки и конфигурация ---
# class Settings(BaseSettings):
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Ключ берется из переменных окружения

class Settings(BaseSettings):
    openai_api_key: SecretStr

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
settings = Settings()
api_key = settings.openai_api_key.get_secret_value()

GPT_MODEL: str = "gpt-4o"  # Модель по умолчанию

# settings = Settings()
# # --- Модель для POST-запроса ---

# --- Эндпоинт для обработки запроса ---
@app.post("/ask-gpt")
async def ask_gpt(request):
    try:
        # Проверка наличия текста
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Текст не может быть пустым")

        # Формируем промпт с дополнительным контекстом (опционально)
        prompt = f"""
        Текст :
        '{request.text}'
        """
        system_message = '''Ты система суммаризации. Твоя задачи суммаризировать текст, которой будет подан на вход.
        Не пиши ничего лишнего. В ответ пиши только суммаризированный текст. Строго соблюдай эту инструкцию.
        '''
        # Отправляем запрос к ChatGPT
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[{"role": "system", "content": system_message},
                      {"role": "user", "content": prompt}],
            temperature=0.7,  # Контроль креативности (0-2)
            max_tokens=500    # Максимальная длина ответа
        )

        # Извлекаем ответ
        gpt_response = response.choices[0].message["content"].strip()
        return {"response": gpt_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")