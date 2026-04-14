from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Импортируем прослойку
from playwright.async_api import async_playwright

app = FastAPI()

# --- ДОБАВЬ ЭТОТ БЛОК ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Разрешает запросы с любых адресов. Для разработки это ок.
    allow_credentials=True,
    allow_methods=["*"], # Разрешает все методы (GET, POST и т.д.)
    allow_headers=["*"], # Разрешает любые заголовки
)
# ------------------------

@app.get("/verify")
async def verify_rtn(protocol_number: str):
    async with async_playwright() as p:
        # Твой существующий код...
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"]) # На Railway часто нужен --no-sandbox
        page = await browser.new_page()

        # 1. Переход на страницу
        await page.goto("https://qr.gosnadzor.ru/prombez")

        # 2. Поиск поля и ввод номера
        await page.fill('input[formcontrolname="protocolNumber"]', protocol_number)
        await page.click('button.btn')

        # 3. Ожидание результата
        try:
            await page.wait_for_selector('app-protocol-item', timeout=5000)

            # Парсим ФИО и статус
            fio = await page.inner_text('mat-card-subtitle')
            content = await page.inner_text('mat-card-content')
            is_valid = "НЕДЕЙСТВИТЕЛЕН" not in content  # Проверка на красный текст

            await browser.close()
            return {"status": "success", "fio": fio, "is_valid": is_valid, "raw_data": content}
        except:
            await browser.close()
            return {"status": "not_found"}
