from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from datetime import datetime
import json
import os

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

pending_reset = False  # флаг подтверждения

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def money_handler(update, context):
    global pending_reset
    text = update.message.text.replace(" ", "")

    # подтверждение сброса
    if pending_reset and text == "RESET":
        save_data([])
        pending_reset = False
        update.message.reply_text("❌ Все записи удалены")
        return

    pending_reset = False  # любое другое сообщение сбрасывает ожидание

    if not (text.startswith("+") or text.startswith("-")):
        return

    try:
        amount = int(text)
    except ValueError:
        return

    data = load_data()
    data.append({
        "user": update.message.from_user.first_name,
        "amount": amount,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M")
    })
    save_data(data)

    total = sum(item["amount"] for item in data)
    sign = "➕" if amount > 0 else "➖"

    update.message.reply_text(
        f"{sign} Записано: {amount}\n"
        f"💰 Общая сумма: {total}"
    )

def sum_command(update, context):
    data = load_data()
    total = sum(item["amount"] for item in data)
    update.message.reply_text(f"💰 Общая сумма: {total}")

def list_command(update, context):
    data = load_data()
    if not data:
        update.message.reply_text("Записей пока нет")
        return

    text = "📄 История:\n"
    for item in data:
        text += f'{item["date"]} — {item["user"]}: {item["amount"]}\n'

    update.message.reply_text(text)

def reset_command(update, context):
    global pending_reset
    pending_reset = True
    update.message.reply_text(
        "⚠️ Вы уверены, что хотите удалить ВСЕ записи?\n"
        "Напишите: RESET"
    )

def start(update, context):
    update.message.reply_text(
        "Привет! 👋\n\n"
        "➕ +СУММА — добавить\n"
        "➖ -СУММА — вычесть\n\n"
        "/sum — общая сумма\n"
        "/list — история\n"
        "/reset — сброс (с подтверждением)"
    )

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("sum", sum_command))
    dp.add_handler(CommandHandler("list", list_command))
    dp.add_handler(CommandHandler("reset", reset_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, money_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
