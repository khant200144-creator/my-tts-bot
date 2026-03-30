import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import edge_tts
import asyncio
import os

# ဤနေရာတွင် သင့် Token အမှန်ကို ပြန်ထည့်ပေးပါ
TOKEN =('8657151202:AAFJrtxoqiyvXmontyYT-XFzqkbcUrq4JkA')
bot = telebot.TeleBot(TOKEN)

user_voices = {}
user_speeds = {} # အမြန်နှုန်း မှတ်သားရန် အသစ်ထည့်ထားသည်

THIHA_VOICE = 'my-MM-ThihaNeural'
NILAR_VOICE = 'my-MM-NilarNeural'

# အမြန်နှုန်းများကို အသံမပျက်စေရန် အချိုးကျ ညှိထားခြင်း
SPEED_MAP = {
    "speed_1x": "+0%",   # ပုံမှန်
    "speed_2x": "+25%",  # မြန်
    "speed_3x": "+50%",  # တော်တော်မြန်
    "speed_4x": "+75%",  # အရမ်းမြန်
    "speed_5x": "+100%"  # အမြန်ဆုံး (ဒါထက်ပိုရင် အသံပျက်သွားနိုင်ပါသည်)
}

# စာသားကို အသံနှင့် အမြန်နှုန်းပါ ပြောင်းပေးမည့် လုပ်ဆောင်ချက်
async def generate_audio(text, voice, rate, filename):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(filename)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "မင်္ဂလာပါ။ Myanmar TTS Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "🗣 အသံပြောင်းချင်ရင် /voice ကို နှိပ်ပါ။\n"
        "⚡️ အမြန်နှုန်းပြောင်းချင်ရင် /speed ကို နှိပ်ပါ။"
    )
    bot.reply_to(message, welcome_text)

# အသံရွေးရန် ခလုတ်
@bot.message_handler(commands=['voice'])
def choose_voice(message):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("👦 သီဟ", callback_data="voice_thiha")
    btn2 = InlineKeyboardButton("👧 နီလာ", callback_data="voice_nilar")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "အသုံးပြုလိုသော အသံကို ရွေးချယ်ပါ:", reply_markup=markup)

# အမြန်နှုန်းရွေးရန် ခလုတ် (1x to 5x)
@bot.message_handler(commands=['speed'])
def choose_speed(message):
    markup = InlineKeyboardMarkup(row_width=3)
    b1 = InlineKeyboardButton("1x (Normal)", callback_data="speed_1x")
    b2 = InlineKeyboardButton("2x", callback_data="speed_2x")
    b3 = InlineKeyboardButton("3x", callback_data="speed_3x")
    b4 = InlineKeyboardButton("4x", callback_data="speed_4x")
    b5 = InlineKeyboardButton("5x", callback_data="speed_5x")
    markup.add(b1, b2, b3, b4, b5)
    bot.send_message(message.chat.id, "အသံ အမြန်နှုန်းကို ရွေးချယ်ပါ:", reply_markup=markup)

# ခလုတ်များ နှိပ်သည့်အခါ အလုပ်လုပ်မည့်အပိုင်း
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # အသံခလုတ် နှိပ်လျှင်
    if call.data.startswith("voice_"):
        if call.data == "voice_thiha":
            user_voices[call.from_user.id] = THIHA_VOICE
            bot.answer_callback_query(call.id, "သီဟ အသံကို ရွေးချယ်လိုက်ပါပြီ။")
            bot.send_message(call.message.chat.id, "👦 သီဟ အသံကို ပြောင်းလဲပြီးပါပြီ။")
        elif call.data == "voice_nilar":
            user_voices[call.from_user.id] = NILAR_VOICE
            bot.answer_callback_query(call.id, "နီလာ အသံကို ရွေးချယ်လိုက်ပါပြီ။")
            bot.send_message(call.message.chat.id, "👧 နီလာ အသံကို ပြောင်းလဲပြီးပါပြီ။")
            
    # အမြန်နှုန်းခလုတ် နှိပ်လျှင်
    elif call.data.startswith("speed_"):
        speed_val = SPEED_MAP.get(call.data, "+0%")
        user_speeds[call.from_user.id] = speed_val
        label = call.data.split("_")[1] # ဥပမာ - '1x', '2x'
        bot.answer_callback_query(call.id, f"{label} အမြန်နှုန်း ရွေးလိုက်ပါပြီ။")
        bot.send_message(call.message.chat.id, f"⚡️ အမြန်နှုန်းကို {label} သို့ ပြောင်းလဲပြီးပါပြီ။ စာရိုက်ထည့်လို့ရပါပြီ။")

# စာရိုက်ထည့်လျှင် အသံပြန်ပို့ပေးမည့်အပိုင်း
@bot.message_handler(func=lambda message: True)
def text_to_speech(message):
    try:
        text = message.text
        msg = bot.reply_to(message, "အသံပြောင်းနေပါတယ်။ ခဏစောင့်ပေးပါ ⏳...")
        
        # User ရွေးထားတဲ့အသံ နှင့် အမြန်နှုန်းကို ယူမည်
        voice = user_voices.get(message.from_user.id, THIHA_VOICE)
        rate = user_speeds.get(message.from_user.id, "+0%")
        file_name = f"voice_{message.from_user.id}.mp3"
        
        # အသံပြောင်းခြင်း
        asyncio.run(generate_audio(text, voice, rate, file_name))
        
       # အသံဖိုင် ပို့ခြင်း (Download ဆွဲရန် လွယ်ကူစေရန် သီချင်းဖိုင်အနေဖြင့် ပို့မည်)
        with open(file_name, "rb") as audio:
            bot.send_audio(message.chat.id, audio, title="Myanmar AI Voice")
        # အမှိုက်ရှင်းခြင်း
        os.remove(file_name)
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, "တောင်းပန်ပါတယ်။ စာသားကို အသံပြောင်းရာမှာ အမှားအယွင်းဖြစ်သွားပါတယ်။")

print("Bot is running with Voices and Speeds...")
bot.infinity_polling()