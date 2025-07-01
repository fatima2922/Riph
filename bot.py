from flask import Flask
import threading
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext
)
import json

import os
TOKEN = os.getenv("TOKEN")
users = {}
referrals = {}
tasks = [
    {"text": f"مهمة {i+1}", "url": f"https://shrinkme.ink/example{i+1}"}
    for i in range(47)
]

def load_data():
    global users, referrals
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
        with open("referrals.json", "r") as f:
            referrals = json.load(f)
    except:
        users, referrals = {}, {}

def save_data():
    with open("users.json", "w") as f:
        json.dump(users, f)
    with open("referrals.json", "w") as f:
        json.dump(referrals, f)

def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        users[user_id] = {"points": 0.0, "completed": [], "referrals": []}
        if args:
            ref_id = args[0]
            if ref_id != user_id and ref_id in users:
                users[ref_id]["points"] += 0.001  # 10% إحالة
                users[ref_id]["referrals"].append(user_id)
                referrals[user_id] = ref_id

    save_data()
    update.message.reply_text("أهلاً بيك في بوت المهام!\nاكتب /tasks عشان تبدأ.")

def tasks_cmd(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        update.message.reply_text("أرسل /start أولاً.")
        return

    keyboard = []
    for i, task in enumerate(tasks):
        if i >= 47: break
        if i not in users[user_id]["completed"]:
            keyboard.append([InlineKeyboardButton(task["text"], url=task["url"], callback_data=f"done_{i}")])

    if not keyboard:
        update.message.reply_text("أنجزت كل المهام اليومية ❤️")
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("اضغط على المهام وارجع اضغط تم بعد كل واحدة:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = query.data

    if data.startswith("done_"):
        task_index = int(data.split("_")[1])
        if task_index not in users[user_id]["completed"]:
            users[user_id]["completed"].append(task_index)
            users[user_id]["points"] += 0.007  # ربح المستخدم
            save_data()
            query.answer("تم احتساب المهمة ✅")
            query.edit_message_text("تم احتساب المهمة ✅")
        else:
            query.answer("أنجزت هذه المهمة من قبل ❌")

def balance(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        update.message.reply_text("أرسل /start أولاً.")
        return
    points = users[user_id]["points"]
    update.message.reply_text(f"رصيدك: {points:.3f} دولار 💰")

def referrals_cmd(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        update.message.reply_text("أرسل /start أولاً.")
        return
    ref_link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
    total_refs = len(users[user_id]["referrals"])
    update.message.reply_text(f"رابط إحالتك:\n{ref_link}\n\nعدد الإحالات: {total_refs}")

def main():
    load_data()
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tasks", tasks_cmd))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("referrals", referrals_cmd))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()
    
app = Flask(__name__)

@app.route('/')
def home():
    app = Flask(__name__)

@app.route('/')
def home():
    return "البوت شغال 🟢"

@app.route('/task/<task_id>')
def task(task_id):
    return f"تم استقبال المهمة رقم {task_id}"

def run_flask():
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    main()

