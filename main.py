import sqlite3
import os

from datetime import datetime
# from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# from telegram import InputMediaPhoto
from dotenv import load_dotenv

load_dotenv()

# Access your token
TOKEN = os.getenv("TOKEN")

BOT_USERNAME = 'kwhy_bot'
DATABASE_NAME = 'kwhy_bot.db'

def create_connection():
    connection = None
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

    return connection

def create_tables(connection):
    cursor = connection.cursor()
    create_inbox_table_query = '''
    CREATE TABLE IF NOT EXISTS inbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        message_type TEXT,
        message_text TEXT,
        username TEXT,
        date TEXT
    );
    '''
    create_outbox_table_query = '''
    CREATE TABLE IF NOT EXISTS outbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        message_type TEXT,
        message_text TEXT,
        user_bot TEXT,
        date TEXT
    );
    '''
    cursor.execute(create_inbox_table_query)
    cursor.execute(create_outbox_table_query)
    connection.commit()

def insert_inbox_message(connection, chat_id, message_type, message_text, username, date):
    cursor = connection.cursor()
    insert_message_query = '''
    INSERT INTO inbox (chat_id, message_type, message_text, username, date)
    VALUES (?, ?, ?, ?, ?);
    '''
    data_tuple = (chat_id, message_type, message_text, username, date)
    cursor.execute(insert_message_query, data_tuple)
    connection.commit()

def insert_outbox_message(connection, chat_id, message_type, message_text, user_bot, date):
    cursor = connection.cursor()
    insert_message_query = '''
    INSERT INTO outbox (chat_id, message_type, message_text, user_bot, date)
    VALUES (?, ?, ?, ?, ?);
    '''
    data_tuple = (chat_id, message_type, message_text, user_bot, date)
    cursor.execute(insert_message_query, data_tuple)
    connection.commit()

#Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('welkom, gweh kwhy.. tanya aja apa yg mau kao minta (jawab bener opsional)')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """
        Daftar Perintah yang Tersedia:

        /hello - Untuk menyapa bot
        /sup - Untuk mengirim salam
        /meisenpai - Untuk memanggil Mei senpai
        /ei - Untuk memuji Raiden Ei
        /cat - Untuk melihat gambar kucing
        /acheronbuild - Untuk informasi build Acheron
        /pelabuild - Untuk informasi build Pela
    """
    await update.message.reply_text(message)
    # await update.message.reply_text('/hello /sup /mei senpai')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('not implemented yet')


#Respon
def handle_response(text: str) -> str:

    processed: str = text.lower()

    if '/hello' in processed:
        return 'yoo'
    if '/sup' in processed:
        return 'gud'
    # if 'mei' in processed:
    #     return 'waipu'
    if '/meisenpai' in processed:
        return 'Mei senpaiiiii waipuu'
    if '/ei' in processed:
        return 'Raiden Ei is waipu'
    if '/cat' in processed:
        return '?'
    if '/acheronbuild' in processed:
        return 'acheron build'
    if '/pelabuild' in processed:
        return 'pela build'
    
    return 'wat du yu min'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    chat_id: int = update.message.chat.id
    username: str = update.message.from_user.username if update.message.from_user.username else "Unknown"
    date: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save incoming message to inbox table
    connection = create_connection()
    create_tables(connection)
    insert_inbox_message(connection, chat_id, message_type, text, username, date)
    connection.close()

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)

    # Save outgoing response to outbox table
    connection = create_connection()
    if response == 'Mei senpaiiiii waipuu':
        # Send a cat image
        await context.bot.send_photo(chat_id=chat_id, photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwqooNeB4C003io14HucSRI392OijzMmKmsdL-tUpwSw&s')
    if response == 'Acheron is waipu':
        # Send a cat image
        await context.bot.send_photo(chat_id=chat_id, photo='https://assetsio.gnwcdn.com/honkai-star-rail-acheron-kit.jpg?width=1200&height=1200&fit=bounds&quality=70&format=jpg&auto=webp')
    if response == 'Raiden Ei is waipu':
        # Send a cat image
        await context.bot.send_photo(chat_id=chat_id, photo='https://static.animecorner.me/2022/10/raiden-shogun-ei-1024x576.png')
    if response == 'acheron build':
        # Send a cat image
        await context.bot.send_photo(chat_id=chat_id, photo='https://upload-os-bbs.hoyolab.com/upload/2024/03/27/362645635/7f4da39c48fc7e9119836c7ca09a23cf_117758249250086852.png?x-oss-process=image%2Fresize%2Cs_1000%2Fauto-orient%2C0%2Finterlace%2C1%2Fformat%2Cwebp%2Fquality%2Cq_80')
    if response == 'pela build':
        # Send a cat image
        await context.bot.send_photo(chat_id=chat_id, photo='https://pbs.twimg.com/media/F6UYtuAXIAA02ly?format=jpg&name=4096x4096')
    else:
        insert_outbox_message(connection, chat_id, message_type, response, BOT_USERNAME, date)
        connection.close()
        await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Kwhy awaken')
    app = Application.builder().token(TOKEN).build()

    #Command
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    #Message
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Error
    app.add_error_handler(error)

    #Polls the bot
    print('Poll....')
    app.run_polling(poll_interval=5)