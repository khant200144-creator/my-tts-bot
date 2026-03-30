import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import edge_tts
import asyncio
import os
from flask import Flask
from threading import Thread
('8657151202:AAFJrtxoqiyvXmontyYT-XFzqkbcUrq4JkA')
bot = telebot.TeleBot(TOKEN)

user_voices = {}
user_speeds = {}

THIHA_VOICE = 'my-MM-ThihaNeural'
NILAR_VOICE = 'my-MM-NilarNeural'

SPEED_MAP = {
    "speed_1x": "+0%",
    "speed_2x": "+25%",
    "speed_3x": "+50%",
    "speed_4x": "+75%",
    "speed_5x": "+100%"
}

async def generate_audio(text, voice, rate, filename):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(filename)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "မင်္ဂလာပါ။ Myanmar TTS Bot မှ ကြိုဆိုပါတယ်။\n\n🗣 အသံပြောင်းချင်ရင် /voice ကို နှိပ်ပါ။\n⚡️ အမြန်နှုန်းပြောင်းချင်ရင် /speed ကို နှိပ်ပါ။"
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['voice'])
def choose_voice(message):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("👦 သီဟ", callback_data="voice_thiha")
    btn2 = InlineKeyboardButton("👧 နီလာ", callback_data="voice_nilar")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "အသုံးပြုလိုသော အသံကို ရွေးချယ်ပါ:", reply_markup=markup)

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

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("voice_"):
        if call.data == "voice_thiha":
            user_voices[call.from_user.id] = THIHA_VOICE
            bot.answer_callback_query(call.id, "သီဟ အသံကို ရွေးချယ်လိုက်ပါပြီ။")
            bot.send_message(call.message.chat.id, "👦 သီဟ အသံကို ပြောင်းလဲပြီးပါပြီ။")
        elif call.data == "voice_nilar":
            user_voices[call.from_user.id] = NILAR_VOICE
            bot.answer_callback_query(call.id, "နီလာ အသံကို ရွေးချယ်လိုက်ပါပြီ။")
            bot.send_message(call.message.chat.id, "👧 နီလာ အသံကို ပြောင်းလဲပြီးပါပြီ။")
            
    elif call.data.startswith("speed_"):
        speed_val = SPEED_MAP.get(call.data, "+0%")
        user_speeds[call.from_user.id] = speed_val
        label = call.data.split("_")[1]
        bot.answer_callback_query(call.id, f"{label} အမြန်နှုန်း ရွေးလိုက်ပါပြီ။")
        bot.send_message(call.message.chat.id, f"⚡️ အမြန်နှုန်းကို {label} သို့ ပြောင်းလဲပြီးပါပြီ။")

@bot.message_handler(func=lambda message: True)
def text_to_speech(message):
    try:
        text = message.text
        msg = bot.reply_to(message, "အသံပြောင်းနေပါတယ်။ ခဏစောင့်ပေးပါ ⏳...")
        
        voice = user_voices.get(message.from_user.id, THIHA_VOICE)
        rate = user_speeds.get(message.from_user.id, "+0%")
        file_name = f"voice_{message.from_user.id}.mp3"
        
        asyncio.run(generate_audio(text, voice, rate, file_name))
        
        with open(file_name, "rb") as audio:
            bot.send_audio(message.chat.id, audio, title="Myanmar AI Voice")
            
        os.remove(file_name)
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, "တောင်းပန်ပါတယ်။ စာသားကို အသံပြောင်းရာမှာ အမှားအယွင်းဖြစ်သွားပါတယ်။")

# Render Free Plan အတွက် "Web Service" အဖြစ် ဟန်ဆောင်မည့်အပိုင်း
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running successfully on Render!"

def run_server():
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

if name == "__main__":
    server_thread = Thread(target=run_server)server_thread.start()
    print("Bot is running...")
    bot.infinity_polling()
