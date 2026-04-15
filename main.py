import re # Добавь этот импорт в самое начало для поиска даты
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright

app = FastAPI()

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
            
            # Ищем дату в формате ДД.ММ.ГГГГ с помощью регулярного выражения
            date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', content)
            found_date = date_match.group(0) if date_match else None

            await browser.close()
            return {
                "status": "success",
                "fio": fio.strip(),
                "date": found_date, # Теперь дата прилетит отдельным полем!
                "is_valid": "НЕДЕЙСТВИТЕЛЕН" not in content,
                "raw_content": content 
            }
        except Exception as e:
            await browser.close()
            return {"status": "not_found", "error": str(e)}
