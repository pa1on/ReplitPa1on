from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from moviepy.editor import VideoFileClip
import os
import logging

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь квадратное видео, и я пришлю тебе кружочек.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Получено видео")
    video = update.message.video

    if video.width != video.height:
        await update.message.reply_text("Видео должно быть квадратным!")
        return

    file_id = video.file_id
    file = await context.bot.get_file(file_id)
    input_path = f"{file_id}.mp4"
    output_path = f"circle_{file_id}.mp4"

    await file.download_to_drive(input_path)

    try:
        clip = VideoFileClip(input_path)
        duration = clip.duration
        safe_duration = max(0.5, duration - 0.2)
        clip = clip.subclip(0, safe_duration)
        clip = clip.resize((240, 240))
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=24)

        with open(output_path, 'rb') as f:
            await update.message.reply_video_note(video_note=f)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))

if __name__ == "__main__":
    print("Бот запущен")
    app.run_polling()
