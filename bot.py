from flask import Flask
import threading
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext
)
import json
import os
import requests
import datetime
import time

TOKEN = "7709139375:AAHKZoteAJbdUj9LTjX6381cIU3CRplZnXk"
API_KEY = "a88b2ee9b26afcf7d099485214f98bac3f7f3360"
API_BASE =  "https://zegalinks.com/api/v1"
users = {}
referrals = {}p
last_task_time = {}
pending_tasks = []  # مهام تحت التحقق
MIN_WITHDRAW = 10.0
withdraw_requests = []

# مهمات مع الرابط اللي طلبتيه مضاف يدويًا
tasks = [
    {"text": "مهمة 1", "url": "http://link.zegalinks.com/lUUtg"},
    # ممكن تضيفي مهام ثانية هنا لو عايزة
]

def load_data():
    global users, referrals, last_task_time, pending_tasks
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = {}

    try:
        with open("referrals.json", "r") as f:
            referrals = json.load(f)
    except:
        referrals = {}

    try:
        with open("last_task_time.json", "r") as f:
            raw = json.load(f)
            last_task_time = {k: datetime.datetime.fromisoformat(v) for k,v in raw.items()}
    except:
        last_task_time = {}

    try:
        with open("pending_tasks.json", "r") as f:
            pending_tasks = json.load(f)
    except:
        pending_tasks = []

def save_data():
    with open("users.json", "w") as f:
        json.dump(users, f)
    with open("referrals.json", "w") as f:
        json.dump(referrals, f)
    with open("last_task_time.json", "w") as f:
        serializable = {k: v.isoformat() for k,v in last_task_time.items()}
        json.dump(serializable, f)
    with open("pending_tasks.json", "w") as f:
        json.dump(pending_tasks, f)

def get_shortlink_earnings(shortlink):
    try:
        resp = requests.get(f"{API_BASE}/stats/link/{shortlink}", headers={"Authorization": f"Bearer {API_KEY}"})
        if resp.status_code == 200:
            data = resp.json()
            return float(data['data']['revenue'])
        else:
            return 0.0
    except:
        return 0.0

def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        users[user_id] = {"points": 0.0, "completed": [], "referrals": []}
        if args:
            ref_id = args[0]
            if ref_id != user_id and ref_id in users:
                users[ref_id]["points"] += 0.007
                users[ref_id]["referrals"].append(user_id)
                referrals[user_id] = ref_id

    save_data()
    keyboard = [
        ["/tasks", "/balance"],
        ["/referrals", "/withdraw"],
        ["/mytasks"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "أهلاً بيك في بوت المهام!\nاختار أمر من الأزرار تحت 👇",
        reply_markup=reply_markup
    )

def tasks_cmd(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        update.message.reply_text("أرسل /start أولاً.")
        return

    page = 0
    if context.args:
        try:
            page = int(context.args[0])
        except:
            page = 0

    tasks_per_page = 10
    start_index = page * tasks_per_page
    end_index = start_index + tasks_per_page

    available_tasks = [i for i in range(len(tasks)) if i not in users[user_id]["completed"]]
    page_tasks = available_tasks[start_index:end_index]

    keyboard = []
    for i in page_tasks:
        keyboard.append([
            InlineKeyboardButton(tasks[i]["text"], url=tasks[i]["url"]),
            InlineKeyboardButton("✅ تم", callback_data=f"done_{i}")
        ])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}"))
    if end_index < len(available_tasks):
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    if not keyboard:
        update.message.reply_text("أنجزت كل المهام اليومية ❤️")
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("لتنفيذ المهمة وكسب النقاط: اضغط على الرابط، انتظر االعد التنازلي ، كمّل المطلوب واتاكد من اعلى الشاشه انك وصلت step5 وبعد اتمام الخطوات ح تستلم رابط يوتيوب اذا وصلت اليوتيوب كدا انت مهمتك انتهت ارجع اعمل تم فالبوت"),
            reply_markup=reply_marku
        )

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = query.data
    now = datetime.datetime.now()

    if data.startswith("done_"):
        # منع تنفيذ أكثر من مهمة في اليوم
        if user_id in last_task_time:
            elapsed = now - last_task_time[user_id]
            if elapsed.total_seconds() < 24 * 3600:
                query.answer("😴 أنهيت المهام اليوم، تعال بكرة مرة تانية!", show_alert=True)
                return

        task_index = int(data.split("_")[1])
        if task_index in users[user_id]["completed"]:
            query.answer("أنجزت هذه المهمة من قبل ❌")
            return

        short_code = tasks[task_index]["url"].split("/")[-1]
        earned = get_shortlink_earnings(short_code)
        task_reward = 0.01

        if earned >= task_reward:
            users[user_id]["completed"].append(task_index)
            users[user_id]["points"] += task_reward * 0.7
            if user_id in referrals:
                ref_id = referrals[user_id]
                users[ref_id]["points"] += task_reward * 0.1

            if len(users[user_id]["completed"]) == len(tasks):
                last_task_time[user_id] = now

            save_data()
            query.answer("تم احتساب المهمة ✅")
            query.edit_message_text("تم احتساب المهمة ✅")
        else:
            pending_tasks.append({
                "user_id": user_id,
                "task_index": task_index,
                "timestamp": now.isoformat(),
                "before_earning": earned
            })
            save_data()
            query.answer("مهمتك تحت التحقق، سيتم مراجعتها قريباً.")
            query.edit_message_text("مهمتك تحت التحقق، انتظر التحديث خلال دقائق.")

    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        tasks_per_page = 10
        start_index = page * tasks_per_page
        end_index = start_index + tasks_per_page

        available_tasks = [i for i in range(len(tasks)) if i not in users[user_id]["completed"]]
        page_tasks = available_tasks[start_index:end_index]

        keyboard = []
        for i in page_tasks:
            keyboard.append([
                InlineKeyboardButton(tasks[i]["text"], url=tasks[i]["url"]),
                InlineKeyboardButton("✅ تم", callback_data=f"done_{i}")
            ])

        nav_buttons = []
        if start_index > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}"))
        if end_index < len(available_tasks):
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page+1}"))

        if nav_buttons:
            keyboard.append(nav_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)

        if keyboard:
            query.edit_message_text(
                "from flask import Flask
import threading
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext
)
import json
import os
import requests
import datetime
import time

TOKEN = "7709139375:AAHKZoteAJbdUj9LTjX6381cIU3CRplZnXk"
API_KEY = "a88b2ee9b26afcf7d099485214f98bac3f7f3360"
API_BASE =  "https://zegalinks.com/api/v1"
users = {}
referrals = {}p
last_task_time = {}
pending_tasks = []  # مهام تحت التحقق
MIN_WITHDRAW = 10.0
withdraw_requests = []

# مهمات مع الرابط اللي طلبتيه مضاف يدويًا
tasks = [
    {"text": "مهمة 1", "url": "http://link.zegalinks.com/lUUtg"},
    # ممكن تضيفي مهام ثانية هنا لو عايزة
]

def load_data():
    global users, referrals, last_task_time, pending_tasks
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = {}

    try:
        with open("referrals.json", "r") as f:
            referrals = json.load(f)
    except:
        referrals = {}

    try:
        with open("last_task_time.json", "r") as f:
            raw = json.load(f)
            last_task_time = {k: datetime.datetime.fromisoformat(v) for k,v in raw.items()}
    except:
        last_task_time = {}

    try:
        with open("pending_tasks.json", "r") as f:
            pending_tasks = json.load(f)
    except:
        pending_tasks = []

def save_data():
    with open("users.json", "w") as f:
        json.dump(users, f)
    with open("referrals.json", "w") as f:
        json.dump(referrals, f)
    with open("last_task_time.json", "w") as f:
        serializable = {k: v.isoformat() for k,v in last_task_time.items()}
        json.dump(serializable, f)
    with open("pending_tasks.json", "w") as f:
        json.dump(pending_tasks, f)

def get_shortlink_earnings(shortlink):
    try:
        resp = requests.get(f"{API_BASE}/stats/link/{shortlink}", headers={"Authorization": f"Bearer {API_KEY}"})
        if resp.status_code == 200:
            data = resp.json()
            return float(data['data']['revenue'])
        else:
            return 0.0
    except:
        return 0.0

def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        users[user_id] = {"points": 0.0, "completed": [], "referrals": []}
        if args:
            ref_id = args[0]
            if ref_id != user_id and ref_id in users:
                users[ref_id]["points"] += 0.007
                users[ref_id]["referrals"].append(user_id)
                referrals[user_id] = ref_id

    save_data()
    keyboard = [
        ["/tasks", "/balance"],
        ["/referrals", "/withdraw"],
        ["/mytasks"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "أهلاً بيك في بوت المهام!\nاختار أمر من الأزرار تحت 👇",
        reply_markup=reply_markup
    )

def tasks_cmd(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        update.message.reply_text("أرسل /start أولاً.")
        return

    page = 0
    if context.args:
        try:
            page = int(context.args[0])
        except:
            page = 0

    tasks_per_page = 10
    start_index = page * tasks_per_page
    end_index = start_index + tasks_per_page

    available_tasks = [i for i in range(len(tasks)) if i not in users[user_id]["completed"]]
    page_tasks = available_tasks[start_index:end_index]

    keyboard = []
    for i in page_tasks:
        keyboard.append([
            InlineKeyboardButton(tasks[i]["text"], url=tasks[i]["url"]),
            InlineKeyboardButton("✅ تم", callback_data=f"done_{i}")
        ])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}"))
    if end_index < len(available_tasks):
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    if not keyboard:
        update.message.reply_text("أنجزت كل المهام اليومية ❤️")
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "ا"افتح الرابط واستنى شوية، حتظهر ليك خطوات (زي الانتظار، الضغط على زر، أو تأكيد).
كمل كل الخطوات لحد ما توصل Step 5.
لما يوصلك زر (الرابط جاهز) أو (ادخل يوتيوب)، كدا المهمة تمت ✅
لو طلعت من الصفحة قبل الخطوة الأخيرة، ما حتتحسب المهمة ❌"",
            reply_markup=reply_marku
        )

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = query.data
    now = datetime.datetime.now()

    if data.startswith("done_"):
        # منع تنفيذ أكثر من مهمة في اليوم
        if user_id in last_task_time:
            elapsed = now - last_task_time[user_id]
            if elapsed.total_seconds() < 24 * 3600:
                query.answer("😴 أنهيت المهام اليوم، تعال بكرة مرة تانية!", show_alert=True)
                return

        task_index = int(data.split("_")[1])
        if task_index in users[user_id]["completed"]:
            query.answer("أنجزت هذه المهمة من قبل ❌")
            return

        short_code = tasks[task_index]["url"].split("/")[-1]
        earned = get_shortlink_earnings(short_code)
        task_reward = 0.01

        if earned >= task_reward:
            users[user_id]["completed"].append(task_index)
            users[user_id]["points"] += task_reward * 0.7
            if user_id in referrals:
                ref_id = referrals[user_id]
                users[ref_id]["points"] += task_reward * 0.1

            if len(users[user_id]["completed"]) == len(tasks):
                last_task_time[user_id] = now

            save_data()
            query.answer("تم احتساب المهمة ✅")
            query.edit_message_text("تم احتساب المهمة ✅")
        else:
            pending_tasks.append({
                "user_id": user_id,
                "task_index": task_index,
                "timestamp": now.isoformat(),
                "before_earning": earned
            })
            save_data()
            query.answer("مهمتك تحت التحقق، سيتم مراجعتها قريباً.")
            query.edit_message_text("مهمتك تحت التحقق، انتظر التحديث خلال دقائق.")

    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        tasks_per_page = 10
        start_index = page * tasks_per_page
        end_index = start_index + tasks_per_page

        available_tasks = [i for i in range(len(tasks)) if i not in users[user_id]["completed"]]
        page_tasks = available_tasks[start_index:end_index]

        keyboard = []
        for i in page_tasks:
            keyboard.append([
                InlineKeyboardButton(tasks[i]["text"], url=tasks[i]["url"]),
                InlineKeyboardButton("✅ تم", callback_data=f"done_{i}")
            ])

        nav_buttons = []
        if start_index > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}"))
        if end_index < len(available_tasks):
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page+1}"))

        if nav_buttons:
            keyboard.append(nav_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)

        if keyboard:
            query.edit_message_text("لتنفيذ المهمة وكسب النقاط: اضغط على الرابط، انتظر االعد التنازلي ، كمّل المطلوب واتاكد من اعلى الشاشه انك وصلت step5 وبعد اتمام الخطوات ح تستلم رابط يوتيوب اذا وصلت اليوتيوب كدا انت مهمتك انتهت ارجع اعمل تم فالبوت"),
                reply_markup=reply_markup
            )
        else:
            query.edit_message_text("أنجزت كل المهام اليومية ❤️")
        query.answer()

def check_pending_tasks(context: CallbackContext):
    global pending_tasks, users, referrals, last_task_time

    now = datetime.datetime.now()
    updated = False
    new_pending = []

    for task in pending_tasks:
        user_id = task["user_id"]
        task_index = task["task_index"]
        timestamp = datetime.datetime.fromisoformat(task["timestamp"])
        before = task.get("before_earning", 0.0)

        short_code = tasks[task_index]["url"].split("/")[-1]
        earned = get_shortlink_earnings(short_code)
        task_reward = 0.01

        # تحقق الفرق بين الربح الحالي والقديم
        if earned - before >= task_reward:
            if task_index not in users[user_id]["completed"]:
                users[user_id]["completed"].append(task_index)
                users[user_id]["points"] += task_reward * 0.7
                if user_id in referrals:
                    ref_id = referrals[user_id]
                    users[ref_id]["points"] += task_reward * 0.1
                if len(users[user_id]["completed"]) == len(tasks):
                    last_task_time[user_id] = now
                updated = True
                try:
                    context.bot.send_message(
                        chat_id=int(user_id),
                        text=f"✅ تم التحقق من مهمتك #{task_index + 1} وتمت إضافة الرصيد!"
                    )
                except:
                    pass
        else:
            new_pending.append(task)

    pending_tasks = new_pending
    if updated:
        save_data()

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

app = Flask(__name__)

@app.route('/')
def home():
    return "البوت شغال 🟢"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

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

    # إضافة مهمة تحقق دورية كل 5 دقائق
    job_queue = updater.job_queue
    job_queue.run_repeating(check_pending_tasks, interval=300, first=10)

    keep_alive()
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()",
                reply_markup=reply_markup
            )
        else:
            query.edit_message_text("أنجزت كل المهام اليومية ❤️")
        query.answer()

def check_pending_tasks(context: CallbackContext):
    global pending_tasks, users, referrals, last_task_time

    now = datetime.datetime.now()
    updated = False
    new_pending = []

    for task in pending_tasks:
        user_id = task["user_id"]
        task_index = task["task_index"]
        timestamp = datetime.datetime.fromisoformat(task["timestamp"])
        before = task.get("before_earning", 0.0)

        short_code = tasks[task_index]["url"].split("/")[-1]
        earned = get_shortlink_earnings(short_code)
        task_reward = 0.01

        # تحقق الفرق بين الربح الحالي والقديم
        if earned - before >= task_reward:
            if task_index not in users[user_id]["completed"]:
                users[user_id]["completed"].append(task_index)
                users[user_id]["points"] += task_reward * 0.7
                if user_id in referrals:
                    ref_id = referrals[user_id]
                    users[ref_id]["points"] += task_reward * 0.1
                if len(users[user_id]["completed"]) == len(tasks):
                    last_task_time[user_id] = now
                updated = True
                try:
                    context.bot.send_message(
                        chat_id=int(user_id),
                        text=f"✅ تم التحقق من مهمتك #{task_index + 1} وتمت إضافة الرصيد!"
                    )
                except:
                    pass
        else:
            new_pending.append(task)

    pending_tasks = new_pending
    if updated:
        save_data()

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

app = Flask(__name__)

@app.route('/')
def home():
    return "البوت شغال 🟢"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

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

    # إضافة مهمة تحقق دورية كل 5 دقائق
    job_queue = updater.job_queue
    job_queue.run_repeating(check_pending_tasks, interval=300, first=10)

    keep_alive()
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
