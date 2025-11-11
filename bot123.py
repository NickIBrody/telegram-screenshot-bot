import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
from io import BytesIO

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# СЮДА ПОДСТАВЬ СВОЙ ТОКЕН ОТ BOTFATHER
TOKEN = " "

def take_screenshot(url):
    """Функция для создания скриншота сайта"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        driver.get(url)
        driver.implicitly_wait(10)
        screenshot = driver.get_screenshot_as_png()
        return screenshot
    except Exception as e:
        logger.error(f"Ошибка при создании скриншота: {e}")
        return None
    finally:
        driver.quit()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start"""
    welcome_text = (
        "Отправьте ссылку на сайт (начинающуюся с http:// или https://), "
        "и я пришлю его скриншот.\n\n"
        "По вопросам работы бота обращаться: @werg23p"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщения от пользователя"""
    user_message = update.message.text

    if user_message.startswith(('http://', 'https://')):
        await update.message.reply_text("Создаю скриншот... Пожалуйста, подождите.")

        screenshot = await asyncio.get_event_loop().run_in_executor(
            None, take_screenshot, user_message
        )

        if screenshot:
            await update.message.reply_photo(
                BytesIO(screenshot),
                caption=f"Скриншот для {user_message}"
            )
        else:
            await update.message.reply_text(
                "Не удалось создать скриншот. Проверьте корректность ссылки "
                "или обратитесь к разработчику: @werg23p"
            )
    else:
        await update.message.reply_text("Пожалуйста, отправьте корректную ссылку, начинающуюся с http:// или https://")

def main():
    """Запускает бота"""
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()

