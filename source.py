from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN: Final = os.getenv("MY_TOKEN")
BOT_USERNAME: Final = "@vanhgptbot"

system_mess = SystemMessage(content="Bạn là một trợ lý AI hữu ích")
history = [system_mess]
MAX_RECENT = 9
model = OllamaLLM(model="llama3.1:8b")

# Thiết lập các lệnh
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("start has been called")
    await update.message.reply_text("Xin chào, VietAnh1027 rất vui khi bạn sử dụng bot này, bạn muốn nói về chủ đề gì ?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("help has been called")
    await update.message.reply_text("Bạn hãy chat lên đây câu hỏi hoặc chủ đề mà bạn thắc mắc, mình sẽ trò chuyện và giải đáp giúp bạn!\nVì là 1 Chatbot đơn giản nên nếu bạn thấy mình trả lời không như mong đợi, hãy dùng lệnh /reset để mình được nghỉ ngơi và tiếp tục trò chuyện với bạn ngay sau đó")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history
    history = [system_mess]
    print("reset has been called")
    await update.message.reply_text("Mình đã nghỉ ngơi xong, bạn muốn nói về chủ đề gì ?")

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history
    text = "\n\n".join([mess.content for mess in history])
    await update.message.reply_text(text)

# Bot phản hồi
def handle_response(text: str) -> str:
    global history
    history.append(HumanMessage(content=text))
    history = history[-MAX_RECENT:]

    result = model.invoke(history)
    history.append(AIMessage(content=result))
    return result

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User: ({update.message.chat.id}) in {message_type}: '{text}'")

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot: ', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Lệnh mặc định
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('reset', reset_command))
    app.add_handler(CommandHandler('hist',history_command))

    # Tin nhắn đến
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error
    app.add_error_handler(error)
    print('Polling...')
    app.run_polling(poll_interval=5)