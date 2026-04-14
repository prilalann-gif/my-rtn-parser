FROM python:3.9-slim

# 1. Устанавливаем системные библиотеки, без которых браузер не запустится
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxext6 libxfixes3 librandr2 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. СКАЧИВАЕМ БРАУЗЕР (Это решит твою ошибку из логов!)
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# 4. Запускаем сервер
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
