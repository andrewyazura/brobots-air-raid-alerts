from src import create_bot


def main():
    bot = create_bot()
    bot.updater.start_polling()
    bot.updater.idle()
