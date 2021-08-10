# standard modules
import time
import logging

# third party modules
import yaml
import telegram
from telegram.ext import Updater, CommandHandler


class GotCourtsCheckerBotService:
    def __init__(self, token: str, request_processor: callable) -> None:
        self.updater = Updater(token=token, use_context=True)
        self.request_processor = request_processor

    @staticmethod
    def start(update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"I'm a GotCourtsCheckerBot, chat ID: {update.effective_chat.id}",
        )

    def check(self, update, context):
        prefix = "/check"
        msg = f"{update.message.text} "
        assert msg.startswith(prefix)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self.request_processor(msg[len(prefix) :].strip()),
            parse_mode=telegram.constants.PARSEMODE_MARKDOWN,
        )

    def init_service(self):
        start_handler = CommandHandler("start", self.start)
        check_handler = CommandHandler("check", self.check)

        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(check_handler)

    def run(self):
        # start polling thread
        self.updater.start_polling()
        # initialize an infinite loop to monitor service status
        while True:
            if not self.updater.running:
                logging.error("Service is not running")
            else:
                time.sleep(1)


class GotCourtsCheckerBot:
    """Got Courts Waiter Bot

    Args:
        token (str): telegram Bot token
        config_path (str): path to the YAML config file.
    """

    def __init__(self, token: str, config_path: str):
        self.bot = telegram.Bot(token=token)
        self.config = self.get_config(config_path)

    def get_config(self, config_path: str) -> dict:
        """Load configuration from a YAML file.

        Args:
            config_path (str): path to config location

        Returns:
            dict: configuration dictionary
        """
        with open(config_path, "r") as stream:
            return yaml.safe_load(stream)

    def message_all(self, text: str):
        """Send message to all chat IDs that are present in the config.

        Args:
            text (str): message text
        """
        for chat_id in self.config["chat_ids"]:
            self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=telegram.constants.PARSEMODE_MARKDOWN,
            )
