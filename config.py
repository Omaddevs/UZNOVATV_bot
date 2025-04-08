import telebot
from telebot.types import *
import sqlite3
import speedtest
import os

BASE = {}

conn = sqlite3.connect('database.db',
                       check_same_thread=False,
                       isolation_level=None)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,chat_id INTIGER UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS admins(id INTEGER PRIMARY KEY,chat_id INTIGER UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY,username TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS video(id INTEGER UNIQUE,file_id TEXT,caption TEXT,down INTIGER)")

conn.commit()

ADMIN_ID = Admin_ID 
bot = telebot.TeleBot("BOT TOKEN",parse_mode='html')

back = InlineKeyboardMarkup().add(InlineKeyboardButton(text="🔙 Exit",callback_data='back'))


def add_new_admin(msg):
    if msg.text.isdigit():
        try:
            cursor.execute(f"INSERT INTO admins(chat_id) VALUES({msg.text})")
            conn.commit()
            bot.reply_to(msg,f"<b>✅ Yangi {msg.text} qo'shildi!</b>",reply_markup=back)
        except:
            bot.reply_to(msg,f"<b>❌ oldindan mavjud bo'lgan!</b>",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="➕ Qo'shish",callback_data='new-admin')).add(InlineKeyboardButton(text="🔙 Exit",callback_data='back')))

    else:
        bot.reply_to(msg,f"<b>❌ admin qo'shishda xatolik!</b>",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="➕ Qo'shish",callback_data='new-admin')).add(InlineKeyboardButton(text="🔙 Exit",callback_data='back')))
def add_new_chat(msg):
    if "@" in msg.text:
        try:
            cursor.execute(f"INSERT INTO chats(username) VALUES('{msg.text}')")
            conn.commit()
            bot.reply_to(msg,f"<b>✅ Yangi {msg.text} qo'shildi!</b>",reply_markup=back)
        except:
            bot.reply_to(msg,f"<b>❌ oldindan mavjud bo'lgan kanal!</b>",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="➕ Qo'shish",callback_data='new-chat')).add(InlineKeyboardButton(text="🔙 Exit",callback_data='back')))
    else:
        bot.reply_to(msg,f"<b>❌ kanal qo'shishda xatolik!</b>",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="➕ Qo'shish",callback_data='new-chat')).add(InlineKeyboardButton(text="🔙 Exit",callback_data='back')))

def get_admin(cid):
    admin = cursor.execute(f"SELECT chat_id FROM admins  WHERE chat_id={cid}").fetchone()
    if ADMIN_ID==cid or admin is not None:
        return True
    else:
        return False


def video_key(code):
    key =InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="♻️ Do'stlarga ulashish",url=f"https://t.me/share/url?url=t.me/{bot.get_me().username}?start={code}&text=Eng song'i kinolar toplami!")
    ).add(InlineKeyboardButton(text="❌",callback_data='remove') )
    return key

def add_new_kino_caption(msg):
    if msg.text:
        code = BASE['code']
        file_id = BASE['file_id']
        caption = str(msg.text).replace("'", "||")
        try:
            cursor.execute(f"INSERT INTO video(id, file_id, caption, down) VALUES({code}, '{file_id}', '{caption}', {0})")
            b = bot.send_video(msg.chat.id, file_id, caption=caption.replace("||", "'").replace("%stat", "0").replace("%code", str(code)), reply_markup=video_key(code), protect_content=True).message_id
            bot.send_message(msg.chat.id, f"<b>Kino kodi: {code}</b>", reply_to_message_id=b)
        except Exception as e:
            bot.send_message(msg.chat.id, f"<b>❌ {e}</b>", reply_markup=back)
    else:
        bot.send_message(msg.chat.id, "<b>❌ Bekor qilindi!</b>", reply_markup=back)
def add_new_kino_code(msg):
    text = msg.text
    if text.isdigit():
        BASE['code'] = text
        a = bot.reply_to(msg,"<b>🔖 Kino tafsifini kiriting: %stat | %code</b>")
        bot.register_next_step_handler(a,add_new_kino_caption)
    else:
        bot.send_message(msg.chat.id,"<b>❌ Bekor qilindi!</b>",reply_markup=back)
def add_new_kino(msg):
    if msg.video:
        file_id = msg.video.file_id
        BASE['file_id'] = file_id
        a = bot.reply_to(msg, "<b>Kino kodini kiriting: 12</b>")
        bot.register_next_step_handler(a, add_new_kino_code)
    else:
        bot.send_message(msg.chat.id, "<b>❌ Bekor qilindi!</b>", reply_markup=back)

def delete_kino(msg):
    if msg.text.isdigit():
        code = msg.text
        try:
            cursor.execute("DELETE FROM video WHERE id=?", (code,))
            conn.commit()
            bot.reply_to(msg, f"<b>✅ Kino {code} muvaffaqiyatli o'chirildi!</b>", reply_markup=back)
        except Exception as e:
            bot.reply_to(msg, f"<b>❌ Xato yuz berdi: {e}</b>", reply_markup=back)
    else:
        bot.reply_to(msg, f"<b>❌ Bekor qilindi!</b>", reply_markup=back)

def join_chat_key():
    list = cursor.execute("SELECT * FROM chats").fetchall()
    key = InlineKeyboardMarkup()
    c = 0
    for i in list:
        c+=1
        username = str(i[1]).replace("@","")
        key.add(InlineKeyboardButton(text=f"{c} - kanal",url=f"https://t.me/{username}"))
    key.add(InlineKeyboardButton(text="✅ Tasdiqlash",callback_data="check"))

    return key

def join(user_id):
    list = cursor.execute("SELECT * FROM chats").fetchall()
    if len(list) ==0:
        return True
    c = 0
    for i in list:
        username = str(i[1]).replace("@","")
        print(username)
        try:
            member = bot.get_chat_member(f"{i[1]}", user_id)
        except:
            bot.send_message(user_id,"<b>❌ Kechirasiz botimizdan foydalanishdan oldin ushbu kanallarga a'zo bo'lishingiz kerak.</b>",parse_mode='html',reply_markup=join_chat_key())
            return False
        x = ['member', 'creator', 'administrator']
        if member.status not in x:
            bot.send_message(user_id,"<b>❌ Kechirasiz botimizdan foydalanishdan oldin ushbu kanallarga a'zo bo'lishingiz kerak.</b>",parse_mode='html',reply_markup=join_chat_key())
            return False
        else:
            c+=1
    if c==len(list):
        return True

def server():
    st = speedtest.Speedtest()
    st.config['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    download_speed = st.download() / 10**6
    upload_speed = st.upload() / 10**6
    server = st.get_best_server()
    ping = st.results.ping
    txt = f"<b>🚀 Speed Test Result:\n\n✘ Download Speed: {download_speed:.2f} Mbps\n✘ Upload Speed: {upload_speed:.2f} Mbps\n✘ Ping: {ping} ms</b>"
    return txt
def admin_menu():
    key = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="✍️ Oddiy xabar", callback_data='send_post'),
        InlineKeyboardButton(text="📨 Forward xabar", callback_data='send_for'),
    ).add(
        InlineKeyboardButton(text="📊 Statistika", callback_data='static'),
        InlineKeyboardButton(text="🚀 Server", callback_data='server')
    ).add(
        InlineKeyboardButton(text="📋 Adminlar", callback_data='list_admin'),
        InlineKeyboardButton(text="🔉 Kanallar", callback_data='list_chat'),
    ).add(
        InlineKeyboardButton(text="➕ Kino qo'shish", callback_data='add_new_kino'),
        InlineKeyboardButton(text="➖ Kino o'chirish", callback_data='delete_kino')  # Yangi tugma qo'shildi
    ).add(
        InlineKeyboardButton(text="🔙 Chiqish", callback_data='check'),
    )
    return key



def send_post(msg):
    text = msg.text
    users = cursor.execute("SELECT chat_id FROM users").fetchall()

    for i in users:
        try:
            bot.send_message(i[0],text)
        except:
            pass
    bot.reply_to(msg,"<b>✅ Xabar yuborildi !</b>",reply_markup=back)
def send_for(msg):
    mid = msg.id
    chat_id = msg.chat.id
    users = cursor.execute("SELECT chat_id FROM users").fetchall()
    for i in users:
        try:
            bot.forward_message(i[0],chat_id,mid)
        except:
            pass
    bot.reply_to(msg,"<b>✅ Xabar yuborildi !</b>",reply_markup=back)
