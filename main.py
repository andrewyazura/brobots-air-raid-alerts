from src import create_bot

bot = create_bot()

if __name__ == "__main__":
    bot.updater.start_polling()
    bot.updater.idle()
