import logging
import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import asyncio
from io import BytesIO

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

TOKEN = ""

def take_screenshot(url, delay=0):
    """Функция для создания скриншота сайта с задержкой"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        
        if delay > 0:
            time.sleep(delay)
            
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
        "🔍 *ScreenshotEye Bot* - бот для создания скриншотов сайтов\n\n"
        "💡 *Как использовать:*\n"
        "Просто отправьте ссылку на сайт (начинающуюся с http:// или https://)\n\n"
        "✨ *Функции:*\n"
        "• ⏱ Задержка загрузки (0, 3, 5, 10 сек)\n"
        "• 📊 Прогресс бар при создании скриншота\n\n"
        "По вопросам: @werg23p"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на inline кнопки"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data.startswith("delay_"):
        delay = int(data.split("_")[1])
        url = context.user_data.get('pending_url')
        
        if not url:
            await query.edit_message_text("❌ Ошибка: URL не найден")
            return
        
        progress_messages = [
            "⏳ Запуск браузера... (10%)",
            "🌐 Загрузка страницы... (30%)",
            f"⏱ Ожидание {delay} сек... (50%)" if delay > 0 else "📸 Подготовка... (50%)",
            "📸 Создание скриншота... (80%)",
            "✅ Завершение... (95%)"
        ]
        
        progress_msg = await query.edit_message_text(progress_messages[0])
        
        for i, msg in enumerate(progress_messages[1:], 1):
            await asyncio.sleep(0.5)
            try:
                await progress_msg.edit_text(msg)
            except:
                pass
        
        screenshot = await asyncio.get_event_loop().run_in_executor(
            None, take_screenshot, url, delay
        )
        
        if screenshot:            
            await query.message.reply_photo(
                BytesIO(screenshot),
                caption=f"📸 Скриншот для {url}\n⏱ Задержка: {delay} сек"
            )
            try:
                await progress_msg.delete()
            except:
                pass
        else:
            await progress_msg.edit_text(
                "❌ Не удалось создать скриншот. Проверьте корректность ссылки."
            )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщения от пользователя"""
    user_message = update.message.text
    
    if user_message.startswith(('http://', 'https://')):
        context.user_data['pending_url'] = user_message
        
        keyboard = [
            [
                InlineKeyboardButton("⚡ Сразу (0 сек)", callback_data="delay_0"),
                InlineKeyboardButton("⏱ 3 сек", callback_data="delay_3")
            ],
            [
                InlineKeyboardButton("⏱ 5 сек", callback_data="delay_5"),
                InlineKeyboardButton("⏱ 10 сек", callback_data="delay_10")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ *Выберите задержку перед скриншотом:*\n\n"
            "Задержка полезна для полной загрузки:\n"
            "• Анимаций и переходов\n"
            "• Динамического контента\n"
            "• Изображений и видео",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте корректную ссылку, начинающуюся с http:// или https://\n\n"
            "Используйте /start для помощи"
        )

def main():
    """Запускает бота"""
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Бот запущен и готов к работе!")
    application.run_polling()

if __name__ == '__main__':
    main()

