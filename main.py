from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, BaseSettings
import openai

app = FastAPI()

# --- Настройки и конфигурация ---
class Settings(BaseSettings):
    OPENAI_API_KEY: str  # Ключ берется из переменных окружения
    GPT_MODEL: str = "gpt-3.5-turbo"  # Модель по умолчанию

settings = Settings()

# --- Модель для POST-запроса ---
class UserRequest(BaseModel):
    text: str  # Текст, который нужно передать в GPT

# --- Эндпоинт для обработки запроса ---
@app.post("/ask-gpt")
async def ask_gpt(request: UserRequest):
    try:
        # Проверка наличия текста
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Текст не может быть пустым")

        # Формируем промпт с дополнительным контекстом (опционально)
        prompt = f"""
        Пользователь написал: '{request.text}'
        Ответь подробно, но кратко:
        """

        # Отправляем запрос к ChatGPT
        openai.api_key = settings.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model=settings.GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # Контроль креативности (0-2)
            max_tokens=500    # Максимальная длина ответа
        )

        # Извлекаем ответ
        gpt_response = response.choices[0].message["content"].strip()
        return {"response": gpt_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")