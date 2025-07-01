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
    {"text": "مهمة رقم 1", "url": "https://shrinkme.ink/9O1OS"},
    {"text": "مهمة رقم 2", "url": "https://shrinkme.ink/xXlm"},
    {"text": "مهمة رقم 3", "url": "https://shrinkme.ink/EMBUU7w"},
    {"text": "مهمة رقم 4", "url": "https://shrinkme.ink/nF8IX"},
    {"text": "مهمة رقم 5", "url": "https://shrinkme.ink/gGgT80"},
    {"text": "مهمة رقم 6", "url": "https://shrinkme.ink/VEj2"},
    {"text": "مهمة رقم 7", "url": "https://shrinkme.ink/JbZf0"},
    {"text": "مهمة رقم 8", "url": "https://shrinkme.ink/dMMa"},
    {"text": "مهمة رقم 9", "url": "https://shrinkme.ink/k2Bfr"},
    {"text": "مهمة رقم 10", "url": "https://shrinkme.ink/ghx52U"},
    {"text": "مهمة رقم 11", "url": "https://shrinkme.ink/zqLR2"},
    {"text": "مهمة رقم 12", "url": "https://shrinkme.ink/Wn4E0JL"},
    {"text": "مهمة رقم 13", "url": "https://shrinkme.ink/0L3WwMB"},
    {"text": "مهمة رقم 14", "url": "https://shrinkme.ink/lv7nSzlT"},
    {"text": "مهمة رقم 15", "url": "https://shrinkme.ink/Gggpj1zT"},
    {"text": "مهمة رقم 16", "url": "https://shrinkme.ink/JmvWlqQ"},
    {"text": "مهمة رقم 17", "url": "https://shrinkme.ink/F0NQx2"},
    {"text": "مهمة رقم 18", "url": "https://shrinkme.ink/QOoPsr"},
    {"text": "مهمة رقم 19", "url": "https://shrinkme.ink/yMqF"},
    {"text": "مهمة رقم 20", "url": "https://shrinkme.ink/qyqt3B"},
    {"text": "مهمة رقم 21", "url": "https://shrinkme.ink/0NDUW52z"},
    {"text": "مهمة رقم 22", "url": "https://shrinkme.ink/ORKTjI8S"},
    {"text": "مهمة رقم 23", "url": "https://shrinkme.ink/SfIoDU63"},
    {"text": "مهمة رقم 24", "url": "https://shrinkme.ink/1B8nKoM1"},
    {"text": "مهمة رقم 25", "url": "https://shrinkme.ink/qdcr55"},
    {"text": "مهمة رقم 26", "url": "https://shrinkme.ink/Wq1gr"},
    {"text": "مهمة رقم 27", "url": "https://shrinkme.ink/h8caZnD"},
    {"text": "مهمة رقم 28", "url": "https://shrinkme.ink/efUt3hq"},
    {"text": "مهمة رقم 29", "url": "https://shrinkme.ink/qSWg8bnW"},
    {"text": "مهمة رقم 30", "url": "https://shrinkme.ink/irWxQG"},
    {"text": "مهمة رقم 31", "url": "https://shrinkme.ink/HkxsvN3"},
    {"text": "مهمة رقم 32", "url": "https://shrinkme.ink/xZ6nWZ"},
    {"text": "مهمة رقم 33", "url": "https://shrinkme.ink/HKl9v4h"},
    {"text": "مهمة رقم 34", "url": "https://shrinkme.ink/9FmLumk"},
    {"text": "مهمة رقم 35", "url": "https://shrinkme.ink/USmcO3"},
    {"text": "مهمة رقم 36", "url": "https://shrinkme.ink/kLCmZWn"},
    {"text": "مهمة رقم 37", "url": "https://shrinkme.ink/ZNV9e"},
    {"text": "مهمة رقم 38", "url": "https://shrinkme.ink/YRUJszxb"},
    {"text": "مهمة رقم 39", "url": "https://shrinkme.ink/cvsucprO"},
    {"text": "مهمة رقم 40", "url": "https://shrinkme.ink/YH3wOeFl"},
    {"text": "مهمة رقم 41", "url": "https://shrinkme.ink/ZJ7w"},
    {"text": "مهمة رقم 42", "url": "https://shrinkme.ink/FhudML"},
    {"text": "مهمة رقم 43", "url": "https://shrinkme.ink/1ew9xj"},
    {"text": "مهمة رقم 44", "url": "https://shrinkme.ink/zLcnh8w"},
    {"text": "مهمة رقم 45", "url": "https://shrinkme.ink/ymlvCqR"},
    {"text": "مهمة رقم 46", "url": "https://shrinkme.ink/NqDS"},
    {"text": "مهمة رقم 47", "url": "https://shrinkme.ink/IibhcAjc"},
    {"text": "مهمة رقم 48", "url": "https://shrinkme.ink/UKR43U"},
    {"text": "مهمة رقم 49", "url": "https://shrinkme.ink/A6OPvK"},
    {"text": "مهمة رقم 50", "url": "https://shrinkme.ink/HfLW1rxX"},
    {"text": "مهمة رقم 51", "url": "https://shrinkme.ink/gQtJjgX"},
    {"text": "مهمة رقم 52", "url": "https://shrinkme.ink/N368"},
    {"text": "مهمة رقم 53", "url": "https://shrinkme.ink/7yuMOM"},
    {"text": "مهمة رقم 54", "url": "https://shrinkme.ink/BmKn6Y"},
    {"text": "مهمة رقم 55", "url": "https://shrinkme.ink/dQej11u"},
    {"text": "مهمة رقم 56", "url": "https://shrinkme.ink/ocsuLS"},
    {"text": "مهمة رقم 57", "url": "https://shrinkme.ink/wRE7"},
    {"text": "مهمة رقم 58", "url": "https://shrinkme.ink/dpUO0"},
    {"text": "مهمة رقم 59", "url": "https://shrinkme.ink/3OThCPeS"},
    {"text": "مهمة رقم 60", "url": "https://shrinkme.ink/wt1M"},
    {"text": "مهمة رقم 61", "url": "https://shrinkme.ink/IfNeT0"},
    {"text": "مهمة رقم 62", "url": "https://shrinkme.ink/CDgBcG"},
    {"text": "مهمة رقم 63", "url": "https://shrinkme.ink/BthnvSBY"},
    {"text": "مهمة رقم 64", "url": "https://shrinkme.ink/NB9kf0g"},
    {"text": "مهمة رقم 65", "url": "https://shrinkme.ink/V4rZ"},
    {"text": "مهمة رقم 66", "url": "https://shrinkme.ink/gxyk2Y"},
    {"text": "مهمة رقم 67", "url": "https://shrinkme.ink/mvTpoGjf"},
    {"text": "مهمة رقم 68", "url": "https://shrinkme.ink/Tdrds"},
    {"text": "مهمة رقم 69", "url": "https://shrinkme.ink/GgKyQb"},
    {"text": "مهمة رقم 70", "url": "https://shrinkme.ink/J6WY"},
    {"text": "مهمة رقم 71", "url": "https://shrinkme.ink/2aCygi"},
    {"text": "مهمة رقم 72", "url": "https://shrinkme.ink/0QGBH"},
    {"text": "مهمة رقم 73", "url": "https://shrinkme.ink/eo2bW"},
    {"text": "مهمة رقم 74", "url": "https://shrinkme.ink/CuFdLst"},
    {"text": "مهمة رقم 75", "url": "https://shrinkme.ink/yeDF9l"},
    {"text": "مهمة رقم 76", "url": "https://shrinkme.ink/FkkeA6"},
    {"text": "مهمة رقم 77", "url": "https://shrinkme.ink/bM3Qw0eK"},
    {"text": "مهمة رقم 78", "url": "https://shrinkme.ink/8rCszg"},
    {"text": "مهمة رقم 79", "url": "https://shrinkme.ink/eUHhni9f"},
    {"text": "مهمة رقم 80", "url": "https://shrinkme.ink/ar3uD"},
    {"text": "مهمة رقم 81", "url": "https://shrinkme.ink/Rt9hriiC"},
    {"text": "مهمة رقم 82", "url": "https://shrinkme.ink/qhY5S5nS"},
    {"text": "مهمة رقم 83", "url": "https://shrinkme.ink/2pUtZ"},
    {"text": "مهمة رقم 84", "url": "https://shrinkme.ink/q8X5"},
    {"text": "مهمة رقم 85", "url": "https://shrinkme.ink/oh1y"},
    {"text": "مهمة رقم 86", "url": "https://shrinkme.ink/d4f2iN"},
    {"text": "مهمة رقم 87", "url": "https://shrinkme.ink/SBKD72w2"},
    {"text": "مهمة رقم 88", "url": "https://shrinkme.ink/msfUa4ik"},
    {"text": "مهمة رقم 89", "url": "https://shrinkme.ink/sIGR7"},
    {"text": "مهمة رقم 90", "url": "https://shrinkme.ink/VZv0qD"},
    {"text": "مهمة رقم 91", "url": "https://shrinkme.ink/ad61VKd"},
    {"text": "مهمة رقم 92", "url": "https://shrinkme.ink/RsZeVZMQ"},
    {"text": "مهمة رقم 93", "url": "https://shrinkme.ink/bzpHDl"},
    {"text": "مهمة رقم 94", "url": "https://shrinkme.ink/1cwb"},
    {"text": "مهمة رقم 95", "url": "https://shrinkme.ink/FnDw4eHi"},
    {"text": "مهمة رقم 96", "url": "https://shrinkme.ink/zzv29Vs"},
    {"text": "مهمة رقم 97", "url": "https://shrinkme.ink/qFjt7"},
    {"text": "مهمة رقم 98", "url": "https://shrinkme.ink/Ril1tU"},
    {"text": "مهمة رقم 99", "url": "https://shrinkme.ink/14RRg"},
    {"text": "مهمة رقم 100", "url": "https://shrinkme.ink/SF5e"},
    {"text": "مهمة رقم 101", "url": "https://shrinkme.ink/MmlZERKZ"},
    {"text": "مهمة رقم 102", "url": "https://shrinkme.ink/uSGd2Eqb"},
    {"text": "مهمة رقم 103", "url": "https://shrinkme.ink/6Uv1ltp"},
    {"text": "مهمة رقم 104", "url": "https://shrinkme.ink/vgxaDv"},
    {"text": "مهمة رقم 105", "url": "https://shrinkme.ink/b3HHr"},
    {"text": "مهمة رقم 106", "url": "https://shrinkme.ink/ceytZa"},
    {"text": "مهمة رقم 107", "url": "https://shrinkme.ink/wLOUZuO"},
    {"text": "مهمة رقم 108", "url": "https://shrinkme.ink/QyjD"},
    {"text": "مهمة رقم 109", "url": "https://shrinkme.ink/1oGhP"},
    {"text": "مهمة رقم 110", "url": "https://shrinkme.ink/yuIFHza"},
    {"text": "مهمة رقم 111", "url": "https://shrinkme.ink/8pIHeyva"},
    {"text": "مهمة رقم 112", "url": "https://shrinkme.ink/dogK27zY"},
    {"text": "مهمة رقم 113", "url": "https://shrinkme.ink/g1YoxVX"},
    {"text": "مهمة رقم 114", "url": "https://shrinkme.ink/q6zby"},
    {"text": "مهمة رقم 115", "url": "https://shrinkme.ink/q0eQ"},
    {"text": "مهمة رقم 116", "url": "https://shrinkme.ink/71sN8r"},
    {"text": "مهمة رقم 117", "url": "https://shrinkme.ink/gH7lhv"},
    {"text": "مهمة رقم 118", "url": "https://shrinkme.ink/wOmhf21"},
    {"text": "مهمة رقم 119", "url": "https://shrinkme.ink/au8NmkP"},
    {"text": "مهمة رقم 120", "url": "https://shrinkme.ink/5qui"},
    {"text": "مهمة رقم 121", "url": "https://shrinkme.ink/X1B2VBJS"},
    {"text": "مهمة رقم 122", "url": "https://shrinkme.ink/7o5umxk"},
    {"text": "مهمة رقم 123", "url": "https://shrinkme.ink/UuNWTwz6"},
    {"text": "مهمة رقم 124", "url": "https://shrinkme.ink/G9hmB1a"},
    {"text": "مهمة رقم 125", "url": "https://shrinkme.ink/Fvp57F"},
    {"text": "مهمة رقم 126", "url": "https://shrinkme.ink/9HVBQbh"},
    {"text": "مهمة رقم 127", "url": "https://shrinkme.ink/yZEY"},
    {"text": "مهمة رقم 128", "url": "https://shrinkme.ink/4KTFiRK"},
    {"text": "مهمة رقم 129", "url": "https://shrinkme.ink/EDVjnf"},
    {"text": "مهمة رقم 130", "url": "https://shrinkme.ink/76RD"}
]

MIN_WITHDRAW = 10.0  # الحد الأدنى للسحب بالدولار
withdraw_requests = []  # نخزن فيه طلبات السحب
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
                users[ref_id]["points"] += 0.007  # 10% إحالة
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
        if i not in users[user_id]["completed"]:
            keyboard.append([
                InlineKeyboardButton(task["text"], url=task["url"]),
                InlineKeyboardButton("✅ تم", callback_data=f"done_{i}")
            ])

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
    ref_link = f"https://t.me/Righ_righbot?start={user_id}"
    total_refs = len(users[user_id]["referrals"])
    update.message.reply_text(f"رابط إحالتك:\n{ref_link}\n\nعدد الإحالات: {total_refs}")
def mytasks(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        update.message.reply_text("أرسل /start أولاً.")
        return

    total_tasks = len(tasks)
    completed_tasks = len(users[user_id]["completed"])
    remaining_tasks = total_tasks - completed_tasks
    points = users[user_id]["points"]

    update.message.reply_text(
        f"أنجزت {completed_tasks} من أصل {total_tasks} مهمة ✅\n"
        f"باقي ليك {remaining_tasks} مهمة 🔁\n"
        f"رصيدك الكلي: {points:.3f} دولار 💰"
    )
def withdraw(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        update.message.reply_text("أرسل /start أولاً.")
        return

    balance = users[user_id]["points"]
    if balance < MIN_WITHDRAW:
        update.message.reply_text(f"الحد الأدنى للسحب هو {MIN_WITHDRAW} دولار. رصيدك الحالي: {balance:.3f} دولار.")
        return

    withdraw_requests.append({"user_id": user_id, "amount": balance})
    users[user_id]["points"] = 0.0
    save_data()
    update.message.reply_text("تم تسجيل طلب السحب الخاص بك، سيتم مراجعته خلال 24 ساعة 💸") 
def main():
    load_data()
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tasks", tasks_cmd))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("referrals", referrals_cmd))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("mytasks", mytasks))
    dp.add_handler(CommandHandler("withdraw", withdraw))
    updater.start_polling()
    updater.idle()

app = Flask(__name__)

@app.route('/')
def home():
    return "البوت شغال 🟢"

@app.route('/task/<task_id>')
def task(task_id):
    return f"تم استقبال المهمة رقم {task_id}"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    main()
