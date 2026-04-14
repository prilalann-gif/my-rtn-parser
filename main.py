from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright

app = FastAPI()

# Разрешаем запросы с твоего Flutter-приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/verify")
async def verify_rtn(protocol_number: str):
    async with async_playwright() as p:
        # Добавлены аргументы для стабильной работы на Railway
        browser = await p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page()

        try:
            await page.goto("https://qr.gosnadzor.ru/prombez")
            await page.fill('input[formcontrolname="protocolNumber"]', protocol_number)
            await page.click('button.btn')

            await page.wait_for_selector('app-protocol-item', timeout=5000)

            fio = await page.inner_text('mat-card-subtitle')
            content = await page.inner_text('mat-card-content')
            is_valid = "НЕДЕЙСТВИТЕЛЕН" not in content

            await browser.close()
            return {"status": "success", "fio": fio, "is_valid": is_valid, "raw_data": content}
        except Exception as e:
            await browser.close()
            return {"status": "not_found", "error": str(e)}
