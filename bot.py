import zipfile
import itertools
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from io import BytesIO
import asyncio
import os
import zlib

TOKEN = '5445531176:AAGwd6pVM-UoDrNos3R00QSlr0KuffkZLMY'
GROUP_CHAT_ID = -1001921678002

os.system("clear")

def generate_passwords():
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    length = 1
    while True:
        for password in itertools.product(chars, repeat=length):
            yield ''.join(password)
        length += 1

def crack_zip_password(zip_file_bytes):
    try:
        with zipfile.ZipFile(BytesIO(zip_file_bytes), 'r') as zip_ref:
            for password in generate_passwords():
                try:
                    zip_ref.extractall(pwd=bytes(password, 'utf-8'))
                    return password
                except (RuntimeError, zlib.error, zipfile.BadZipFile):
                    continue
    except zipfile.BadZipFile:
        return None
    return None

def is_zip_password_protected(zip_file_bytes):
    try:
        with zipfile.ZipFile(BytesIO(zip_file_bytes)) as zip_ref:
            file_list = zip_ref.namelist()
            if not file_list:
                return False
            
            with zip_ref.open(file_list[0]) as file:
                file.read(1)
            return False
    except RuntimeError:
        return True
    except zipfile.BadZipFile:
        return False

async def handle_document(update: Update, context: CallbackContext):
    file = update.message.document
    file_obj = await context.bot.get_file(file.file_id)
    file_bytes = await file_obj.download_as_bytearray()

    if is_zip_password_protected(file_bytes):
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="File ZIP diproteksi. Mencoba memecahkan password...")
        
        password = await asyncio.get_event_loop().run_in_executor(None, crack_zip_password, file_bytes)

        if password:
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Password ditemukan: {password}")
        else:
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="Password tidak dapat ditemukan.")
    else:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="File ZIP tidak diproteksi dengan password.")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.Document.MimeType("application/zip"), handle_document))
    application.run_polling()

if __name__ == '__main__':
    main()
