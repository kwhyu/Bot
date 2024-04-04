
###############################################################
#Head#
###############################################################

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from datetime import datetime
import mysql.connector
import os
# from telegram import InputMediaPhoto
from dotenv import load_dotenv

load_dotenv()

# Access your token
TOKEN = os.getenv("TOKEN")

BOT_USERNAME = 'kwhy_bot'

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = ""
# os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

user_menu_selection = {}

###############################################################
#DATABASE#
###############################################################

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print("Connection to MySQL DB successful")
        return connection
    except mysql.connector.Error as e:
        print(f"The error '{e}' occurred")

def create_tables(connection):
    cursor = connection.cursor()

    create_inbox_table_query = '''
    CREATE TABLE IF NOT EXISTS inbox (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chat_id INTEGER,
        message_type VARCHAR(20),
        message_text VARCHAR(255),
        username VARCHAR(255),
        date DATETIME
    );
    '''
    create_outbox_table_query = '''
    CREATE TABLE IF NOT EXISTS outbox (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chat_id INTEGER,
        message_type VARCHAR(255),
        message_text VARCHAR(255),
        user_bot VARCHAR(255),
        date DATETIME
    );
    '''

    create_mahasiswa_table_query = '''
    CREATE TABLE IF NOT EXISTS mahasiswa (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nama VARCHAR(255),
        nim VARCHAR(10),
        alamat VARCHAR(255)
    );
    '''

    create_matakuliah_table_query = '''
    CREATE TABLE IF NOT EXISTS matakuliah (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nama_matakuliah VARCHAR(255),
        kode_matakuliah VARCHAR(10)
    );
    '''
    cursor.execute(create_mahasiswa_table_query)
    cursor.execute(create_matakuliah_table_query)
    cursor.execute(create_inbox_table_query)
    cursor.execute(create_outbox_table_query)

    connection.commit()

def insert_inbox_message(connection, chat_id, message_type, message_text, username, date):
    cursor = connection.cursor()
    insert_message_query = '''
    INSERT INTO inbox (chat_id, message_type, message_text, username, date)
    VALUES (%s, %s, %s, %s, %s);
    '''
    data_tuple = (chat_id, message_type, message_text, username, date)
    cursor.execute(insert_message_query, data_tuple)
    connection.commit()

def insert_outbox_message(connection, chat_id, message_type, message_text, user_bot, date):
    cursor = connection.cursor()
    insert_message_query = '''
    INSERT INTO outbox (chat_id, message_type, message_text, user_bot, date)
    VALUES (%s, %s, %s, %s, %s);
    '''
    data_tuple = (chat_id, message_type, message_text, user_bot, date)
    cursor.execute(insert_message_query, data_tuple)
    connection.commit()

###############################################################
#Default#
###############################################################

#Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('welkom, gweh kwhy.. tanya aja apa yg mau kao minta (jawab bener opsional)')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('get good')

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_keyboard = [
        [InlineKeyboardButton("Cari Mahasiswa", callback_data='cari_mhs')],
        [InlineKeyboardButton("Cari Matakuliah", callback_data='cari_matkul')],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)

    # Kirim pesan dengan custom keyboard
    await update.message.reply_text('Pilih opsi:', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = str(update.message.chat.type)
    text = update.message.text
    chat_id = update.message.chat.id
    username = update.message.from_user.username if update.message.from_user.username else "Unknown"
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

###############################################################
#Menu Mahasiswa#
###############################################################

async def cari_mhs(update: Update, context):
    query = update.callback_query
    await query.answer() 

    # Send message to be edited
    await context.bot.send_message(chat_id=query.message.chat_id, text='Masukkan NIM atau nama mahasiswa yang ingin Anda cari:')

    # Insert message into outbox table
    chat_id = query.message.chat_id
    message_text = 'Masukkan NIM atau nama mahasiswa yang ingin Anda cari:'
    user_bot = BOT_USERNAME
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    connection = create_connection()
    insert_outbox_message(connection, chat_id, "text", message_text, user_bot, date)
    connection.close()

def search_mahasiswa(query: str) -> str:
    # Query the database to search for a student by ID or name
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    sql_query = "SELECT nama, nim, alamat FROM mahasiswa WHERE nim = %s OR nama = %s"
    # cursor.execute(sql_query, (query,))
    cursor.execute(sql_query, (query, query))

    # Get the query result
    result = cursor.fetchone()
    connection.close()

    return result

async def search_nama_nim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nim = update.message.text.strip()
    result = search_mahasiswa(nim)
    if result:
        response_text = f"Mahasiswa ditemukan:\nNama: {result['nama']}\nNIM: {result['nim']}\nAlamat: {result['alamat']}"
    else:
        response_text = "Maaf, mahasiswa tidak ditemukan."
    await update.message.reply_text(response_text)

###############################################################
#Menu Matakuliah#
###############################################################

async def cari_matkul(update: Update, context):
    query = update.callback_query
    await query.answer() 

    await context.bot.send_message(chat_id=query.message.chat_id, text='Masukkan matakuliah yang ingin Anda cari:')
    # Insert message into outbox table
    chat_id = query.message.chat_id
    message_text = 'Masukkan matakuliah yang ingin Anda cari:'
    user_bot = BOT_USERNAME
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    connection = create_connection()
    insert_outbox_message(connection, chat_id, "text", message_text, user_bot, date)
    connection.close()

def search_matakuliah(query: str) -> str:
    # Query the database to search for a student by ID or name
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    sql_query = "SELECT nama_matakuliah, kode_matkul FROM matakuliah WHERE nama_matakuliah = %s"
    cursor.execute(sql_query, (query,))

    # Get the query result
    result = cursor.fetchone()
    connection.close()

    return result

async def search_matkul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    result = search_matakuliah(query)
    if result:
        response_text = f"Matakuliah ditemukan:\nMatakuliah: {result['nama_matakuliah']}\nKode: {result['kode_matkul']}"
    else:
        response_text = "Maaf, matakuliah tidak ditemukan."
    await update.message.reply_text(response_text)


###############################################################
#Main#
###############################################################

async def handle_custom_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected_option = query.data
    user_id = query.from_user.id
    user_menu_selection[user_id] = selected_option
    await query.answer()

    if selected_option == 'cari_mhs':
        await cari_mhs(update, context)
    elif selected_option == 'cari_matkul':
        await cari_matkul(update, context)

async def handle_pre_menu_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_menu_selection:
        del user_menu_selection[user_id]
    await handle_message(update, context)

if __name__ == '__main__':
    print('Kwhy awakened')
    app = Application.builder().token(TOKEN).build()

    # Command
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', menu_command))

    # Message
    app.add_handler(MessageHandler(filters.TEXT, handle_pre_menu_message))
    app.add_handler(MessageHandler(filters.TEXT, search_nama_nim))
    app.add_handler(MessageHandler(filters.TEXT, search_matkul))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Callback
    app.add_handler(CallbackQueryHandler(handle_custom_menu_selection, pattern='^cari_mhs$|^cari_matkul$'))
    # app.add_handler(CallbackQueryHandler(cari_mhs, pattern='^cari_mhs$')) 
    # app.add_handler(CallbackQueryHandler(cari_matkul, pattern='^cari_matkul$'))


    # app.add_handler(CallbackQueryHandler(cari_mhs))
    # app.add_handler(CallbackQueryHandler(cari_matkul))

    # Error
    app.add_error_handler(error)

    # Create connection and tables
    connection = create_connection()
    create_tables(connection)
    connection.close()

    # Polling the bot
    print('Polling....')
    app.run_polling(poll_interval=2)