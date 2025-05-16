import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

TOKEN = os.environ.get("TOKEN")  # یا مستقیماً بنویس "توکن‌ات"

scheduler = BackgroundScheduler()
scheduler.start()

tasks = {}  # حافظه ساده برای ذخیره کارها

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات مدیریت کارها هستم.\nدستور /add برای افزودن کار جدید استفاده کن.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task = ' '.join(context.args)
    tasks.setdefault(user_id, []).append(task)
    await update.message.reply_text(f"✅ کار '{task}' اضافه شد.")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_tasks = tasks.get(user_id, [])
    if not user_tasks:
        await update.message.reply_text("📭 لیست کارت خالیه.")
    else:
        msg = "\n".join([f"{i+1}. {t}" for i, t in enumerate(user_tasks)])
        await update.message.reply_text("📝 لیست کارها:\n" + msg)

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = ' '.join(context.args)
        time_str = msg.split("ساعت")[1].strip().split()[0]
        text = msg.split("ساعت")[1].strip()[len(time_str):].strip()

        hour, minute = map(int, time_str.split(":"))
        now = datetime.datetime.now()
        remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_time < now:
            remind_time += datetime.timedelta(days=1)

        scheduler.add_job(
            send_reminder,
            'date',
            run_date=remind_time,
            args=[context.bot, update.effective_chat.id, text]
        )

        await update.message.reply_text(f"⏰ یادآوری تنظیم شد برای ساعت {time_str}")
    except:
        await update.message.reply_text("❗ فرمت اشتباهه. مثال:\n/remind من ساعت 14:00 آب بخورم")

async def send_reminder(bot, chat_id, text):
    await bot.send_message(chat_id=chat_id, text=f"⏰ یادآوری: {text}")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.photo[-1]
    await update.message.reply_text("✅ فایل دریافت شد. آماده ارسال به دیگران!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))

    app.run_polling()
