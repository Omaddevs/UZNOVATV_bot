from config import *

@bot.message_handler(commands=['panel'])
def admin_handler(msg):
    cid = msg.chat.id
    if(get_admin(cid)):
        bot.send_message(cid,"<b>⚙️ Assalomu alaykum panlega xush kelibsiz!</b>",reply_markup=admin_menu())


@bot.message_handler(commands=['start'])
def welcome(msg):
    cid = msg.chat.id
    id = str(msg.text).replace("/start", "").strip()

    if id.isdigit():
        # Agar id raqam bo'lsa, kino kodi sifatida ishlatamiz
        check = cursor.execute("SELECT * FROM video WHERE id=?", (id,)).fetchone()
        if check is not None:
            try:
                down = check[3] + 1
                bot.send_video(cid, check[1], caption=str(check[2]).replace('||', "'").replace("%stat", str(down)).replace("%code", str(id)), reply_markup=video_key(id))
                cursor.execute("UPDATE video SET down = ? WHERE id = ?", (down, id))
                conn.commit()
            except Exception as e:
                print(e)
        else:
            bot.send_message(cid, "<b>❌ Kino kodi noto'g'ri!</b>")
    else:
        bot.send_message(cid, f"""<b>👋 Assalomu alaykum <a href='tg://user?id={cid}'>{msg.from_user.first_name}</a> botimizga xush kelibsiz.
</b>\nKino kodini @uznovatv dan olasiz\n
<i>✍🏻 Kino kodini yuboring.</i>""")

    try:
        cursor.execute("INSERT INTO users(chat_id) VALUES(?)", (cid,))
        conn.commit()
    except:
        pass






@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    data= call.data
    cid = call.message.chat.id
    mid = call.message.id
    if data=='remove':
        bot.delete_message(cid,mid)
    if data=='static' and get_admin(cid):
        users = cursor.execute("SELECT count(chat_id) FROM users").fetchone()[0]

        bot.edit_message_text(f"""📊 BOT STATISTIKASI

👤 Userlar: {users}

📱 Hammasi bo'lib: {users}""",cid,mid,reply_markup=back)
    elif data=='send_post':
        a = bot.edit_message_text("<b>Kerakli xabar matnini yubring!\nTuri: Text</b>",cid,mid,reply_markup=back)
        bot.register_next_step_handler(a,send_post)
    elif data=='send_for':
        a = bot.edit_message_text("<b>Kerakli xabar matnini yubring!\nTuri: Forward</b>",cid,mid,reply_markup=back)
        bot.register_next_step_handler(a,send_for)
    elif data=='list_admin':
        admins = cursor.execute("SELECT * FROM admins").fetchall()
        key = InlineKeyboardMarkup()
        for i in admins:
            key.add(InlineKeyboardButton(text="❌ "+str(i[1]),callback_data=f"del-{i[1]}"))
        key.add(InlineKeyboardButton(text="➕ Qo'shish",callback_data='new-admin')).add(InlineKeyboardButton(text="🔙 Exit",callback_data='back'))
        bot.edit_message_text("<b>O'chiqmoqchi bo'lgan admini tanlang!</b>",cid,mid,reply_markup=key)
    elif data=='list_chat':
        admins = cursor.execute("SELECT * FROM chats").fetchall()
        key = InlineKeyboardMarkup()
        for i in admins:
            key.add(InlineKeyboardButton(text="❌ "+str(i[1]),callback_data=f"chan-{i[1]}"))
        key.add(InlineKeyboardButton(text="➕ Qo'shish",callback_data='new-chat')).add(InlineKeyboardButton(text="🔙 Exit",callback_data='back'))
        bot.edit_message_text("<b>O'chiqmoqchi bo'lgan kanalni tanlang!</b>",cid,mid,reply_markup=key)
    elif data=='new-admin':
        a = bot.edit_message_text(f"<b>Yangi id kiriting: {cid}</b>",cid,mid,reply_markup=back)
        bot.register_next_step_handler(a,add_new_admin)
    elif data=='new-chat':
        a = bot.edit_message_text(f"<b>Yangi kanal  kiriting: @xunixuz</b>",cid,mid,reply_markup=back)
        bot.register_next_step_handler(a,add_new_chat)
    elif 'del-' in data:
        admin = data.split('-')[1]
        print(admin)
        cursor.execute(f"DELETE FROM admins WHERE chat_id={admin}")
        conn.commit()
        bot.edit_message_text(f"<b>❌ admin {admin} o'chirildi!</b>",cid,mid,reply_markup=back)
    elif 'chan-' in data:
        username = data.split('-')[1]
        cursor.execute(f"DELETE FROM chats WHERE username='{username}'")
        conn.commit()
        bot.edit_message_text(f"<b>❌ kanal {username} o'chirildi!</b>",cid,mid,reply_markup=back)




    elif data=='back':
        bot.clear_step_handler_by_chat_id(cid)
        if(get_admin(cid)):
            bot.edit_message_text("<b>⚙️ Assalomu alaykum panlega xush kelibsiz!</b>",cid,mid,reply_markup=admin_menu())
    elif data=='check':
        if(join(cid)):
            bot.edit_message_text(f"""<b>👋 Assalomu alaykum <a href='tg://user?id={cid}'>{call.from_user.first_name}</a> botimizga xush kelibsiz.
</b>
Kod: @uzbekkinolar_tarjimakinolar 👈shu yerda \n
<i>✍🏻 Kino kodini yuboring.</i>""",cid,mid)
        else:
            bot.delete_message(cid,mid)


    if data=='server':
        a = bot.edit_message_text("<b>🚀 Iltimos kuting...</b>",cid,mid,reply_markup=back).message_id
        print(a)
        bot.edit_message_text(server(),cid,a,reply_markup=back)
    elif data=="add_new_kino":
        a = bot.edit_message_text("<b>➕ Kino video formatda yuboring!</b>",cid,mid,reply_markup=back)
        bot.register_next_step_handler(a,add_new_kino)
    elif data == 'delete_kino':
        a = bot.edit_message_text("<b>➖ Kino kodini kiriting:</b>", cid, mid, reply_markup=back)
        bot.register_next_step_handler(a, delete_kino)


@bot.message_handler(content_types=['text'])
def send_media(message: Message):
    text = message.text
    cid = message.chat.id
    if text.isdigit() and join(cid):
        check = cursor.execute(f"SELECT * FROM video WHERE id={text}").fetchone()
        if check is None:
            bot.reply_to(message, "<b>❌ Kino kodi noto'g'ri!</b>")
        else:
            try:
                down = check[3] + 1
                bot.send_video(cid, check[1], caption=str(check[2]).replace('||', "'").replace("%stat", str(down)).replace("%code", str(text)), reply_markup=video_key(text), protect_content=True)
                cursor.execute(f"UPDATE video SET down = {down} WHERE id = {text}")
                conn.commit()
            except Exception as e:
                print(e)

print(bot.get_me())

def loop():
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)
        bot.send_message(ADMIN_ID,e)
        bot.infinity_polling()

if __name__ == "__main__":
    loop()
