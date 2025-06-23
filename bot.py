

import telebot
from telebot import types

TOKEN = "7332243224:AAHjzIQt048adKi9lXUBDr0su6YSprRR_sw"

bot = telebot.TeleBot(TOKEN)

# قاعدة بيانات مؤقتة (في الواقع تستخدم قاعدة بيانات حقيقية)
users = {}
tasks = {
    1: {"channel": "@channel1", "points": 10},
    2: {"channel": "@channel2", "points": 15},
    3: {"channel": "@channel3", "points": 20},
}
withdraw_requests = []
referrals = {}

# بداية التفاعل مع المستخدم
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    ref = None
    # التحقق من وجود رابط إحالة
    if len(message.text.split()) > 1:
        ref = message.text.split()[1]
    if user_id not in users:
        users[user_id] = {"points": 0, "referred_by": ref, "withdrawn": 0}
        if ref and ref in users:
            users[ref]["points"] += 5  # نقاط إحالة
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("المهام"))
    keyboard.add(types.KeyboardButton("رصيدي"))
    keyboard.add(types.KeyboardButton("سحب أرباحي"))
    keyboard.add(types.KeyboardButton("دعوة أصدقاء"))
    bot.send_message(user_id, "أهلاً بك في بوت المهام الربحي! اختر من القائمة:", reply_markup=keyboard)

# عرض المهام
@bot.message_handler(func=lambda message: message.text == "المهام")
def show_tasks(message):
    user_id = message.from_user.id
    text = "المهام المتاحة:\n"
    for task_id, task in tasks.items():
        text += f"{task_id}. اشترك في القناة {task['channel']} لتحصل على {task['points']} نقطة.\n"
    bot.send_message(user_id, text)

# عرض الرصيد
@bot.message_handler(func=lambda message: message.text == "رصيدي")
def show_balance(message):
    user_id = message.from_user.id
    points = users.get(user_id, {}).get("points", 0)
    bot.send_message(user_id, f"رصيدك الحالي: {points} نقطة.")

# طلب سحب الأرباح
@bot.message_handler(func=lambda message: message.text == "سحب أرباحي")
def request_withdraw(message):
    user_id = message.from_user.id
    points = users.get(user_id, {}).get("points", 0)
    if points < 50:
        bot.send_message(user_id, "رصيدك أقل من 50 نقطة، لا يمكنك طلب السحب الآن.")
        return
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("STC Pay", callback_data="withdraw_stc"))
    keyboard.add(types.InlineKeyboardButton("PayPal", callback_data="withdraw_paypal"))
    keyboard.add(types.InlineKeyboardButton("Vodafone Cash", callback_data="withdraw_vodafone"))
    keyboard.add(types.InlineKeyboardButton("Bayar", callback_data="withdraw_bayar"))
    keyboard.add(types.InlineKeyboardButton("تحويل يدوي", callback_data="withdraw_manual"))
    bot.send_message(user_id, "اختر طريقة السحب:", reply_markup=keyboard)

# التعامل مع اختيار طريقة السحب
@bot.callback_query_handler(func=lambda call: call.data.startswith("withdraw_"))
def handle_withdraw_choice(call):
    user_id = call.from_user.id
    method = call.data.replace("withdraw_", "")
    withdraw_requests.append({"user_id": user_id, "method": method, "points": users[user_id]["points"]})
    users[user_id]["points"] = 0
    bot.answer_callback_query(call.id, f"تم طلب السحب عبر {method}. سيتم التواصل معك قريباً.")
    bot.send_message(user_id, "شكراً لاستخدامك البوت!")

# عرض رابط الإحالة
@bot.message_handler(func=lambda message: message.text == "دعوة أصدقاء")
def show_referral(message):
    user_id = message.from_user.id
    bot.send_message(user_id, f"شارك هذا الرابط مع أصدقائك لكسب نقاط إضافية:\nhttps://t.me/YourBotUsername?start={user_id}")

bot.polling()
        
