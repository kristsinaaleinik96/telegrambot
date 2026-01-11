from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import json
import os

TOKEN = os.getenv("BOT_TOKEN")  # храните токен в переменной окружения
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def handle_number(update, context):
    text = update.message.text.strip()
    try:
        n = int(text)
    except ValueError:
        update.message.reply_text("Пиши только числа!")
        return

    data = load_data()
    data.append(n)
    save_data(data)

    update.message.reply_text(f"Добавлено: {n}\nСумма: {sum(data)}")

def reset(update, context):
    save_data([])
    update.message.reply_text("Сумма сброшена!")

def start(update, context):
    update.message.reply_text(
        "Привет! Пиши числа — бот их суммирует и хранит.\n"
        "/reset — сброс суммы"
    )

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_number))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
