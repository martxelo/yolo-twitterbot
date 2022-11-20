import time

from src import bot

if __name__ == '__main__':

    # start the tweepe api
    api = bot.start_api()

    while True:

        # process all mentions
        bot.proc_all_mentions(api)

        time.sleep(60)
